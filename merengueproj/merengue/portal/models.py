from django.db import models
from django.utils.translation import ugettext_lazy as _

from cmsutils.cache import CachingManager
from transmeta import TransMeta

from merengue.base.models import BaseContent

CATEGORIES = (
    ('primary', _('Primary link')),
    ('secondary', _('Secondary link')),
)


class PortalLink(models.Model):
    """ Primary and secondary portal links """
    __metaclass__ = TransMeta

    name = models.CharField(verbose_name=_('name'), max_length=200)
    content = models.OneToOneField(BaseContent, verbose_name=_('Content'),
                                   blank=True, null=True)
    external_url = models.URLField(verbose_name=_('url'), blank=True, null=True)
    cached_url = models.URLField(verbose_name=_('url'), blank=True,
                                 null=True, editable=False)
    order = models.IntegerField(_('order'), blank=True, null=True)
    category = models.CharField(_('category'), max_length=100, choices=CATEGORIES)

    objects = CachingManager()

    class Meta:
        verbose_name = _('portal link')
        verbose_name_plural = _('portal links')
        translate = ('name', )
        ordering = ('order', )

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return self.cached_url

    def save(self, force_insert=False, force_update=False):
        if self.content is not None:
            self.cached_url = self.content.public_link()
        else:
            self.cached_url = self.external_url
        super(PortalLink, self).save(force_insert, force_update)
