# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models import signals, permalink
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from south.modelsinspector import add_introspection_rules
from stdimage import StdImageField
from tagging.fields import TagField
from transmeta import TransMeta
import sorl

from merengue.base.managers import WorkflowManager
from merengue.base.utils import get_translate_status_list
from merengue.multimedia.managers import MultimediaManager
from merengue.multimedia.fields import VideoField

PHOTO_MEDIA_PREFIX = 'fotos'
VIDEO_MEDIA_PREFIX = 'videos'
PANORAMIC_VIEWS_MEDIA_PREFIX = 'vistas_panoramicas'
IMAGE3D_MEDIA_PREFIX = 'imagenes3d'
AUDIO_MEDIA_PREFIX = 'audios'
FILE_MEDIA_PREFIX = 'files'


class BaseMultimedia(models.Model):
    name = models.CharField(verbose_name=_('name'),
                            max_length=200, db_index=True)
    original_filename = models.CharField(verbose_name=_('name'),
                                         max_length=200, blank=True, null=True,
                                         editable=False)
    creation_date = models.DateTimeField(verbose_name=_('date added'),
                                         auto_now_add=True, editable=False)
    tags = TagField(verbose_name=_('tags'))
    # cached class name from this content
    # this should has null=False, blank=False but in practice this
    # is not possible due to the way the class_name is computed
    # (the object need to get its child class and this is not
    # available until the parent register is saved)
    class_name = models.CharField(verbose_name=_('class name'),
                                  max_length=100, db_index=True,
                                  editable=False, null=True)

    status = models.CharField(_('Publication status'), max_length=20, choices=get_translate_status_list(),
                              default='draft', help_text=_('Enter the current status'), db_index=True,
                              editable=True)
    last_editor = models.ForeignKey(User, verbose_name=_('last editor'), null=True, blank=True, editable=False)
    authors = models.CharField(verbose_name=_('authors'), max_length=200,
                               null=True, blank=True)

    objects = MultimediaManager()

    class Meta:
        verbose_name = _('base multimedia')
        verbose_name_plural = _('base multimedias')
        abstract = False

    def __unicode__(self):
        if getattr(self, 'original_filename', None):
            return u'%s (%s)' % (self.name, self.original_filename)
        else:
            return self.name

    def _get_mixed_name(self):
        if getattr(self, 'original_filename', None):
            return u'%s (%s)' % (self.name, self.original_filename)
        else:
            return self.name
    full_name = property(_get_mixed_name)

    def save(self, **kwargs):
        super(BaseMultimedia, self).save(**kwargs)
        tags_field = self._meta.get_field('tags')
        tags_field._save(instance=self)

    def get_real_instance(self):
        # try looking in our cache
        if hasattr(self, '_real_instance'):
            return self._real_instance

        # python & django magic to get the real attributes of the object
        field_names = self._meta.get_all_field_names()
        keys = [k for k in self.__dict__.keys() if k in field_names]
        # manytomany field to ourselves are hard
        for key in keys:
            field_names.remove(key)

        # get the internal object that is a subclass of ourselves: sounds
        # weird and *it is* weird. See Django subclassing tale for better
        # understanding.
        for field_name in field_names:
            try:
                obj = getattr(self, field_name)
                if isinstance(obj, self.__class__):
                    self._real_instance = obj
                    return self._real_instance
            except (ObjectDoesNotExist, AttributeError, ValueError):
                pass

    def _get_class_name(self):
        real_instance = self.get_real_instance()
        if real_instance is not None:
            return real_instance._meta.module_name
        else:
            return self._meta.module_name

    def get_class_name(self):
        if not self.class_name:
            self.save()
        return self.class_name

    def _save_original_filename(self, file_field):
        """ save original filename. only to be called in subclasses """
        if file_field and isinstance(file_field, UploadedFile):
            self.original_filename = file_field.name

    def get_content(self):
        provinces = self.province_set.all()
        if provinces:
            return provinces[0]
        touristzones = self.touristzone_set.all()
        if touristzones:
            return touristzones[0]
        basecities = self.basecity_set.all()
        if basecities:
            return basecities[0]
        basecontents = self.basecontent_set.all()
        if basecontents:
            return basecontents[0]
        return None

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.get_real_instance())
        return ('base.views.admin_link', [content_type.id, self.id, ''])

    def get_default_preview(self):
        return u'merengue/img/multimedia/image_not_available.jpg'


def get_calculate_class_name(instance):
    instance.class_name = instance._get_class_name()
    try:
        instance.basemultimedia_ptr.class_name = instance.class_name
        base_object = getattr(instance, 'basemultimedia_ptr', None)
        if base_object:
            # only for being coherent with cached value
            base_object.class_name = instance.class_name
    except (ObjectDoesNotExist, AttributeError):
        pass


def handle_base_multimedia_class_name_pre_save(sender, instance, **kwargs):
    if isinstance(instance, BaseMultimedia) and not instance.id:
        get_calculate_class_name(instance)

signals.pre_save.connect(handle_base_multimedia_class_name_pre_save)


class Photo(BaseMultimedia):
    """ Photo """

    __metaclass__ = TransMeta

    image = StdImageField(verbose_name=_('image'),
                          max_length=200,
                          upload_to=PHOTO_MEDIA_PREFIX,
                          thumbnail_size=(200, 200))
    caption = models.TextField(verbose_name=_('caption'), blank=True)
    # only for migration purposes
    plone_uid = models.CharField(verbose_name=_('plone uid'),
                                 max_length=100, db_index=True,
                                 blank=True, null=True, editable=False)

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
        translate = ('caption', )

    def save(self, **kwargs):
        super(Photo, self).save(**kwargs)
        for multimedia_relation in self.multimediarelation_set.all():
            multimedia_relation.save()
        self._save_original_filename(self.image)

        # wether we are adding or modifying an image, the tumbnails are no longer valid.
        # delete it from the image and all its basecontent related items.
        sorl.thumbnail.delete(self.image, delete_file=False)
        # Just in case someone tries to do a sorl thumbnail of the StdImage thumbnail
        sorl.thumbnail.delete(self.image.thumbnail, delete_file=False)

#@FIXME: Duplicate code. base/models.py line 219
    def admin_thumbnail(self):
        file_access_failed = False
        try:
            if not self.image or not self.image.thumbnail or \
               not os.path.exists(self.image.thumbnail.path()):
                file_access_failed = True
        except SuspiciousOperation:
            file_access_failed = True

        if file_access_failed:
            # in development server may not exists thumbnails from
            # production db. See ticket #1659
            return 'file not exists in filesystem'

        thumb_url = self.image.thumbnail.url()
        return u'<a href="%s"><img src="%s" alt="%s" /></a>' % \
                    (self.image.url, thumb_url, self.caption)
    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    objects = WorkflowManager()


class Video(BaseMultimedia):
    """ Video file """
    file = VideoField(verbose_name=_('video file'), upload_to=VIDEO_MEDIA_PREFIX,
                      max_width=480, max_height=360, codec='flv',
                      duration_field='seconds', null=True, blank=True, max_length=200,
                      help_text=_('The file will convert to flv format. It could lose a little of quality'))

    preview = StdImageField(verbose_name=_('preview image'),
                            upload_to=VIDEO_MEDIA_PREFIX,
                            thumbnail_size=(200, 200),
                            blank=True, null=True)
    external_url = models.CharField(verbose_name=_('external url'),
                                     help_text=_('The url of one video from youtube or google-video'),
                                     blank=True, null=True, max_length=255)
    # only for migration purposes
    plone_uid = models.CharField(verbose_name=_('plone uid'),
                                 max_length=100, db_index=True,
                                 blank=True, null=True, editable=False)

    class Meta:
        verbose_name = _('video')
        verbose_name_plural = _('videos')

    def save(self, **kwargs):
        self._save_original_filename(self.file)
        super(Video, self).save(**kwargs)

    def get_absolute_url(self):
        if self.file:
            return self.file.url
        return self.external_url

    def get_configure(self):
        from merengue.theming.models import Theme
        return render_to_string('multimedia/video.js',
                                {'video_info': self,
                                 'MEDIA_URL': settings.MEDIA_URL,
                                 'THEME_MEDIA_URL': Theme.objects.active().get_theme_media_url()})

#@FIXME: Duplicate code. line 292
    def admin_thumbnail(self):
        if self.preview:
            thumb_url = self.preview.thumbnail.url()
            return u'<a href="%s"><img src="%s" alt="video" /></a>' % \
                        (self.preview.url, thumb_url)
        return self
    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    def __unicode__(self):
        return super(Video, self).__unicode__() or self.file.name

    objects = WorkflowManager()


class PanoramicView(BaseMultimedia):
    """ Panoramic view """

    preview = StdImageField(verbose_name=_('preview image'),
                            upload_to=PANORAMIC_VIEWS_MEDIA_PREFIX,
                            thumbnail_size=(200, 200),
                            max_length=255,
                            blank=True, null=True)
    external_url = models.URLField(verify_exists=False, verbose_name=_('url'), max_length=255)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.external_url)

    class Meta:
        verbose_name = _('panoramic view')
        verbose_name_plural = _('panoramic views')

    def save(self, **kwargs):
        self._save_original_filename(self.preview)
        super(PanoramicView, self).save(**kwargs)

#@FIXME: Duplicate code. line 256
    def admin_thumbnail(self):
        if self.preview:
            thumb_url = self.preview.thumbnail.url()
            return u'<a href="%s"><img src="%s" alt="panoramic view" /></a>' % \
                        (self.preview.url, thumb_url)
        return self
    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    objects = WorkflowManager()


class Image3D(BaseMultimedia):
    """ 3D Image """

    file = models.FileField(verbose_name=_('image'),
                            upload_to=IMAGE3D_MEDIA_PREFIX)

    class Meta:
        verbose_name = _('image 3d')
        verbose_name_plural = _('images 3d')

    def save(self, **kwargs):
        self._save_original_filename(self.file)
        super(Image3D, self).save(**kwargs)

    objects = WorkflowManager()


class File(BaseMultimedia):
    """ Attached file """

    file = models.FileField(verbose_name=_('attached file'),
                            max_length=200,
                            upload_to=FILE_MEDIA_PREFIX)

    class Meta:
        verbose_name = _('attached file')
        verbose_name_plural = _('attached files')

    def save(self, **kwargs):
        self._save_original_filename(self.file)
        super(File, self).save(**kwargs)

    objects = WorkflowManager()


class Audio(BaseMultimedia):
    """ Audio file """

    file = models.FileField(verbose_name=_('audio file'),
                            max_length=200,
                            upload_to=AUDIO_MEDIA_PREFIX)

    class Meta:
        verbose_name = _('audio file')
        verbose_name_plural = _('audio files')

    def get_absolute_url(self):
        if self.file:
            return self.file.url
        return ''

    def get_configure(self):
        from merengue.theming.models import Theme
        return render_to_string('multimedia/audio.js',
                                {'audio_info': self,
                                 'MEDIA_URL': settings.MEDIA_URL,
                                 'THEME_MEDIA_URL': Theme.objects.active().get_theme_media_url()})

    def save(self, **kwargs):
        self._save_original_filename(self.file)
        super(Audio, self).save(**kwargs)

    objects = WorkflowManager()


# ----- adding south rules to help introspection -----

rules = [
  (
    (StdImageField, ),
    [],
    {},
  ),
]

add_introspection_rules(rules, ["^stdimage\.fields\.StdImageField"])
