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

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from transmeta import TransMeta

from merengue.base.models import BaseContent
from merengue.perms.models import Role
from merengue.portal.managers import PortalLinksManager
from stdimage import StdImageField


LINK_MEDIA_PREFIX = 'links'


class PortalLink(models.Model):
    """ Primary and secondary portal links """
    __metaclass__ = TransMeta

    name = models.CharField(verbose_name=_('name'), max_length=200)
    content = models.ForeignKey(BaseContent, verbose_name=_('Content'),
                                   blank=True, null=True)
    external_url = models.CharField(verbose_name=_('url'), max_length=200,
                                    blank=True, null=True,
                                    help_text=_('The absolute urls have to write complety: Protocol, domain, query'))
    cached_url = models.CharField(verbose_name=_('url'), max_length=200,
                                  blank=True, null=True, editable=False)
    order = models.IntegerField(_('order'), blank=True, null=True)
    category = models.CharField(_('category'), max_length=100,
                                choices=settings.PORTAL_LINK_CATEGORIES)
    slug = models.SlugField(verbose_name=_('slug'),
                            max_length=200,
                            blank=False,
                            null=False)
    image = StdImageField(verbose_name=_('icon'),
                              null=True, blank=True,
                              upload_to=LINK_MEDIA_PREFIX,
                              help_text=_('The system don\'t resize the icon. You need to upload with the final size'))
    visible_by_roles = models.ManyToManyField(
        Role,
        related_name='visible_links',
        verbose_name=_('visible links'),
        help_text=_('Restrict visibility to some roles'),
        blank=True,
        null=True,
    )

    objects = PortalLinksManager()

    class Meta:
        verbose_name = _('portal link')
        verbose_name_plural = _('portal links')
        translate = ('name', )
        ordering = ('order', )

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return self.cached_url

    def save(self, force_insert=False, force_update=False, using=None):
        if self.content is not None:
            self.cached_url = self.content.public_link()
        else:
            self.cached_url = self.external_url
        super(PortalLink, self).save(force_insert, force_update)
