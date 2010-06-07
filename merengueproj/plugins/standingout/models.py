from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseCategory


class StandingOutCategory(BaseCategory):

    context_variable = models.CharField(verbose_name=_('context variable'), max_length=200)

    class Meta:
        verbose_name = _('standingout category')
        verbose_name_plural = _('standingout categories')


class StandingOut(models.Model):

    obj_content_type = models.ForeignKey(ContentType, verbose_name=_('obj content type'),
                                         related_name='standingout_objects')
    obj_id = models.PositiveIntegerField(_('object id'), db_index=True)
    obj = generic.GenericForeignKey('obj_content_type', 'obj_id')

    related_content_type = models.ForeignKey(ContentType, verbose_name=_('related content type'), null=True, blank=True,
                                             related_name='standingout_relateds')
    related_id = models.PositiveIntegerField(_('related object id'), db_index=True, null=True, blank=True)
    related = generic.GenericForeignKey('related_content_type', 'related_id')

    standing_out_category = models.ForeignKey(StandingOutCategory, verbose_name=_('standing out category'),
                                         null=True, blank=True)

    class Meta:
        ordering = ('related_content_type', 'related_id', 'obj_content_type', 'id')
        unique_together = (('obj_content_type', 'obj_id', 'related_content_type', 'related_id', 'standing_out_category'), )

    def __unicode__(self):
        if not self.related_content_type or not self.related_id:
            return unicode(self.obj)
        return "%s --> %s" %(unicode(self.obj), unicode(self.related))
