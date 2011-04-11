from django.db.models.fields.files import ImageField, ImageFieldFile
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ValidationError
from django.db.models import signals
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from widgets import DelAdminFileWidget
from forms import StdImageFormField
import os
import shutil

from stdimage.globals import DELETED


def _get_thumbnail_filename(filename):
    '''
    Returns the thumbnail name associated to the standard image filename
        * Example: /var/www/myproject/media/img/picture_1.jpeg
            will return /var/www/myproject/media/img/picture_1.thumbnail.jpeg
    '''
    splitted_filename = list(os.path.splitext(filename))
    splitted_filename.insert(1, '.thumbnail')
    thmb_path = ''.join(splitted_filename)
    if not os.path.isabs(thmb_path):
        full_thmb_path = os.path.join(settings.MEDIA_ROOT, thmb_path)
    else:
        full_thmb_path = thmb_path
    if not os.path.exists(full_thmb_path):
        return os.path.splitext(thmb_path)[0] + '.png'
    else:
        return thmb_path


class ThumbnailField:
    '''
    Instances of this class will be used to access data of the
    generated thumbnails
    '''

    def __init__(self, name):
        self.name = name
        self.storage = FileSystemStorage()

    def path(self):
        return self.storage.path(self.name)

    def url(self):
        return self.storage.url(self.name)

    def size(self):
        return self.storage.size(self.name)


class StdImageFieldFile(ImageFieldFile):

    def _get_thumbnail(self):
        '''
        Creates a "thumbnail" object as attribute of the ImageField instance
        Thumbnail attribute will be of the same class of original image, so
        "path", "url"... properties can be used
        '''

        self._require_file()
        thumbnail_filename = _get_thumbnail_filename(self.name)
        thumbnail_field = ThumbnailField(thumbnail_filename)
        thumbnail_path = thumbnail_field.path()
        if not os.path.exists(self.path):
            return thumbnail_field
        if not os.path.exists(thumbnail_path) or\
           os.path.getmtime(self.path) > os.path.getmtime(thumbnail_path):
            self.field._resize_image(self.path, self.field.thumbnail_size, thumbnail_path)
        return thumbnail_field
    thumbnail = property(_get_thumbnail)


class StdImageField(ImageField):
    '''
    Django field that behaves as ImageField, with some extra features like:
        - Auto resizing
        - Automatically generate thumbnails
        - Allow image deletion
    '''
    attr_class = StdImageFieldFile

    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, size=None, thumbnail_size=None, **kwargs):
        '''
        Added fields:
            - size: a tuple containing width and height to resize image, and an optional boolean setting if is wanted forcing that size (None for not resizing).
                * Example: (640, 480, True) -> Will resize image to a width of 640px and a height of 480px. File will be cutted if necessary for forcing te image to have the desired size
            - thumbnail_size: a tuple with same values than `size' (None for not creating a thumbnail
        '''
        params_size = ('width', 'height', 'force')
        for att_name, att in {'size': size, 'thumbnail_size': thumbnail_size}.items():
            if att and (isinstance(att, tuple) or isinstance(att, list)):
                setattr(self, att_name, dict(map(None, params_size, att)))
            else:
                setattr(self, att_name, None)
        super(StdImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)

    def _resize_image(self, filename, size, filenamedst=None):
        '''
        Resizes the image to specified width, height and force option
            - filename: full path of image to resize
            - size: dictionary containing:
                - width: new width
                - height: new height
                - force: if True, image will be cropped to fit the exact size,
                    if False, it will have the bigger size that fits the specified
                    size, but without cropping, so it could be smaller on width or height
            - filenamedst: full path of image to save the resize image
        '''
        WIDTH, HEIGHT = 0, 1
        try:
            from PIL import Image, ImageOps
        except ImportError:
            import Image  # pyflakes:ignore
            import ImageOps  # pyflakes:ignore
        img = Image.open(filename)
        filenamedst = filenamedst or filename
        if img.size[WIDTH] > size['width'] or img.size[HEIGHT] > size['height']:
            if size['force']:
                img = ImageOps.fit(img, (size['width'], size['height']), Image.ANTIALIAS)
            else:
                img.thumbnail((size['width'], size['height']), Image.ANTIALIAS)
            if img.format in ('JPEG', 'PNG'):
                try:
                    img.save(filenamedst, optimize=1)
                except IOError:
                    img.save(filenamedst)
            else:
                try:
                    img.save(filenamedst)
                except KeyError:
                    # PIL no sabe guardar en este formato
                    try:
                        if os.path.exists(filenamedst):
                            os.remove(filenamedst)
                        filenamedst = os.path.splitext(filenamedst)[0] + '.png'
                        img.save(filenamedst)
                        return filenamedst
                    except:
                        raise ValidationError(_('Invalid image format'))

    def _rename_resize_image(self, instance=None, **kwargs):
        '''
        Renames the image, and calls methods to resize and create the thumbnail
        '''
        if not kwargs.get('raw', None):
            if getattr(instance, self.name):
                filename = getattr(instance, self.name).path
                ext = os.path.splitext(filename)[1].lower().replace('jpg', 'jpeg')
                dst = self.generate_filename(instance, '%s_%s%s' % (self.name, instance._get_pk_val(), ext))
                dst_fullpath = os.path.join(settings.MEDIA_ROOT, dst)
                newdst = None
                if os.path.abspath(filename) != os.path.abspath(dst_fullpath):
                    if os.path.exists(filename):
                        os.rename(filename, dst_fullpath)
                        if self.size:
                            newdst = self._resize_image(dst_fullpath, self.size)
                            if newdst:
                                setattr(instance, self.attname, os.path.basename(newdst))
                                dst_fullpath = newdst
                        if self.thumbnail_size:
                            thumbnail_filename = _get_thumbnail_filename(dst_fullpath)
                            shutil.copyfile(dst_fullpath, thumbnail_filename)
                            self._resize_image(thumbnail_filename, self.thumbnail_size)
                        if not newdst:
                            setattr(instance, self.attname, dst)
                        instance.save()

    def _force_create_thumbnail(self, instance=None, **kwargs):
        '''
        Force to create thumbnail a resize
        '''
        if not kwargs.get('raw', None):
            if getattr(instance, self.name):
                filename = getattr(instance, self.name).path
                ext = os.path.splitext(filename)[1].lower().replace('jpg', 'jpeg')
                dst = self.generate_filename(instance, '%s_%s%s' % (self.name, instance._get_pk_val(), ext))
                dst_fullpath = os.path.join(settings.MEDIA_ROOT, dst)
                os.rename(filename, dst_fullpath)
                newdst = None
                if self.size:
                    newdst = self._resize_image(dst_fullpath, self.size)
                    if newdst:
                        setattr(instance, self.attname, os.path.basename(newdst))
                        dst_fullpath = newdst
                thumbnail_filename = _get_thumbnail_filename(dst_fullpath)
                shutil.copyfile(dst_fullpath, thumbnail_filename)
                self._resize_image(thumbnail_filename, self.thumbnail_size)
                if not newdst:
                    setattr(instance, self.attname, dst)
                instance.save()

    def formfield(self, **kwargs):
        '''
        Specify form field and widget to be used on the forms
        '''
        kwargs['widget'] = DelAdminFileWidget
        kwargs['form_class'] = StdImageFormField
        return super(StdImageField, self).formfield(**kwargs)

    def save_form_data(self, instance, data):
        '''
            Overwrite save_form_data to delete images if "delete" checkbox
            is selected
        '''
        if data == DELETED:
            filename = getattr(instance, self.name).path
            if os.path.exists(filename):
                os.remove(filename)
            thumbnail_filename = _get_thumbnail_filename(filename)
            if os.path.exists(thumbnail_filename):
                os.remove(thumbnail_filename)
            setattr(instance, self.name, None)
        else:
            super(StdImageField, self).save_form_data(instance, data)

    def get_db_prep_save(self, value, connection):
        '''
            Overwrite get_db_prep_save to allow saving nothing to the database
            if image has been deleted
        '''
        if value:
            return super(StdImageField, self).get_db_prep_save(value, connection=connection)
        else:
            return u''

    def _anulate_sorl(self, instance=None, **kwargs):
        try:
            import sorl
        except ImportError:
            return
        image = getattr(instance, self.name, None)
        if not image:
            return
        sorl.thumbnail.delete(image, delete_file=False)

    def contribute_to_class(self, cls, name):
        '''
        Call methods for generating all operations on specified signals
        '''
        super(StdImageField, self).contribute_to_class(cls, name)
        signals.post_save.connect(self._rename_resize_image, sender=cls)
        try:
            import sorl  # pyflakes:ignore
            signals.post_save.connect(self._anulate_sorl, sender=cls)
        except ImportError:
            pass
