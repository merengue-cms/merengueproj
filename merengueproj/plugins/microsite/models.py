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

from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from merengue.base.models import BaseContent
from merengue.perms.models import Role
from merengue.section.models import BaseSection
from plugins.microsite.managers import MicroSiteLinkManager
from plugins.microsite.utils import treatment_middelware_microsite
from stdimage import StdImageField
from transmeta import TransMeta


class MicroSite(BaseSection):

    exclude_places = models.TextField(
        _('Exclude template places'),
        blank=True, null=True,
        help_text=_('Select wich template places you want to exclude from your microsite')
        )

    def _content_public_link(self, section, content):
        url_external = reverse(content._public_link_without_section()[0],
                               args=content._public_link_without_section()[1])
        if url_external and url_external[0] == '/':
            url_external = url_external[1:]
        return ('microsite_url', [section.slug, url_external])

    def _document_public_link(self, section, content):
        return ('document_microsite_view', [section.slug, content.pk, content.slug])

    def _menu_public_link(self, ancestors_path, menu):
        reverse_tuple = menu._menu_public_link_without_section(ancestors_path)
        try:
            url_external = reverse(reverse_tuple[0], args=reverse_tuple[1])
            if url_external and url_external[0] == '/':
                url_external = url_external[1:]
        except NoReverseMatch:
            url_external = '/'
        return ('microsite_url', [self.slug, url_external])

    def menu_public_link(self, ancestors_path, menu):
        view, args = self._menu_public_link(ancestors_path, menu)
        url = reverse(view, args=args)
        return treatment_middelware_microsite(url)

    def url_in_section(self, url):
        return '/%s%s' % (self.slug, url)

    def breadcrumbs(self, content=None, context=None):
        if not content:
            # breadcrumbs end here
            return super(MicroSite, self).breadcrumbs()
        url_section = super(MicroSite, self).breadcrumbs_items()
        for name, url in content.breadcrumbs_items():
            if url and url[0] == '/':
                url = url[1:]
            url_section.append((name, reverse("microsite_url", args=(self.slug, url))))
        if url_section:
            url_section[-1] = (url_section[-1][0], '')
        context = context or {}
        context.update({
            'section': self,
            'urls': url_section,
        })
        return render_to_string('microsite/breadcrumbs.html', context)

    def _public_link_without_section(self):
        return ('microsite_view', (self.slug, ))

    def public_link(self):
        url = super(MicroSite, self).public_link()
        return treatment_middelware_microsite(url)

    def body_classes(self):
        bc = super(MicroSite, self).body_classes()
        if self.exclude_places:
            bc += ['hide-%s' % i for i in self.exclude_places.split('\n')]
        return bc

    class Meta:
        verbose_name = _('microsite')
        verbose_name_plural = _('microsites')
        check_slug_uniqueness = True


class MicroSiteLink(models.Model):

    __metaclass__ = TransMeta
    microsite = models.ForeignKey(MicroSite, related_name='micrositelinks')
    name = models.CharField(verbose_name=_('name'), max_length=200)
    content = models.ForeignKey(BaseContent, verbose_name=_('Content'),
                                   blank=True, null=True)
    external_url = models.CharField(verbose_name=_('url'), max_length=200,
                                    blank=True, null=True,
                                    help_text=_('The absolute urls have to write complety: Protocol, domain, query'))
    cached_url = models.CharField(verbose_name=_('url'), max_length=200,
                                  blank=True, null=True, editable=False)
    order = models.IntegerField(_('order'), blank=True, null=True)
    slug = models.SlugField(verbose_name=_('slug'),
                            max_length=200,
                            blank=False,
                            null=False)
    image = StdImageField(verbose_name=_('icon'),
                              null=True, blank=True,
                              upload_to='micrositelinks',
                              help_text=_('The system don\'t resize the icon. You need to upload with the final size'))
    visible_by_roles = models.ManyToManyField(
        Role,
        related_name='visible_micrositelinks',
        verbose_name=_('visible links'),
        help_text=_('Restrict visibility to some roles'),
        blank=True,
        null=True,
    )

    objects = MicroSiteLinkManager()

    class Meta:
        verbose_name = _('microsite link')
        verbose_name_plural = _('microsite links')
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
        super(MicroSiteLink, self).save(force_insert, force_update)
