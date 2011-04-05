from django.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import Base


class CustomPortlet(Base):
    link = models.CharField(
        verbose_name=_('link'), max_length=200,
        help_text=_("Add the link for the block. It can be a internal or external link. " \
                    "Add 'http://' to render the link as external"))
    link_color = models.CharField(verbose_name=_(u'link color'),
                                  max_length=10)
    order = models.IntegerField(verbose_name=_(u'block order'),
                                default=0)
    background = models.FileField(verbose_name=_(u'background'),
                                  upload_to='customportlet')

    class Meta:
        verbose_name = _('Custom portlet')
        verbose_name_plural = _('Custom portlets')
        ordering = ('order', )

    def __unicode__(self):
        return self.name
