from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class StandingOut(models.Model):

    obj_content_type = models.ForeignKey(ContentType, verbose_name=_('obj content type'))
    obj_id = models.PositiveIntegerField(_('object id'), db_index=True)
    obj = generic.GenericForeignKey('obj_content_type', 'obj_id')

    related_content_type = models.ForeignKey(ContentType, verbose_name=_('related content type'), null=True, blank=True)
    related_id = models.PositiveIntegerField(_('related object id'), db_index=True, null=True, blank=True)
    related = generic.GenericForeignKey('related_content_type', 'related_id')

    class Meta:
        ordering = ('related_content_type', 'related_id', 'id')
