# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.utils.translation import gettext_lazy as _

from stdimage.fields import StdImageField


class BaseTiny(models.Model):

    title = models.CharField(_('Title'), max_length=300)
    owner = models.ForeignKey(User, null=True, blank=True, editable=False)

    def __unicode__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return ('tinyimages.views.image_view', [self.id, self.slug])

    class Meta:
        abstract = True

    def _exists_in_fs(self, file_field):
        return file_field.storage.exists(file_field)


class TinyImage(BaseTiny):
    """ image model """

    image = StdImageField(_('Image'), upload_to='tinyimages/img', help_text=_('Select a image to upload'), thumbnail_size=(100, 100, True))

    def exists_in_fs(self):
        return self._exists_in_fs(self.image)

    def delete(self):
        self.image.delete()
        super(TinyImage, self).delete()


class TinyFile(BaseTiny):
    """ file model """
    file = models.FileField(_('File'), upload_to='tinyimages/file', help_text=_('Select a file to upload'), max_length=200)

    def exists_in_fs(self):
        return self._exists_in_fs(self.file)

    def delete(self):
        self.file.delete()
        super(TinyFile, self).delete()
