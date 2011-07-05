# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.block.blocks import Block, ContentBlock, BaseBlock
from merengue.registry import params
from merengue.section.models import BaseSection, Menu
from merengue.section.utils import get_section
from merengue.portal.models import PortalLink
from announcements.models import current_announcements_for_request


class BaseMenuBlock(object):

    config_params = BaseBlock.config_params + [
        params.Integer(name='max_num_level',
                       label=_('maximum number of levels to show'), default=-1)]
    default_caching_params = {
        'enabled': False,
        'only_anonymous': True,
        'vary_on_user': False,
        'timeout': 3600,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def get_max_level(self):
        max_value = self.get_config().get('max_num_level', None)
        if max_value:
            return max_value.get_value()
        return -1


class BaseSingleMenuBlock(BaseMenuBlock):

    config_params = BaseMenuBlock.config_params + [
        params.Integer(name='max_num_items',
                       label=_('maximum number of items without js collapsible'), default=-1)]

    def get_max_num_items(self):
        max_num_items = self.get_config().get('max_num_items', None)
        if max_num_items:
            return max_num_items.get_value()
        return -1


class CoreMenuBlock(BaseSingleMenuBlock, Block):
    name = 'coremenu'
    default_place = 'leftsidebar'
    help_text = _('Renders the Menu')
    verbose_name = _('Core Menu Block')

    def render(self, request, place, context, *args, **kwargs):
        section = get_section(request, context)
        if not section:
            return ''  # renders nothing
        main_menu = section.main_menu
        descendants = None
        if main_menu is not None:
            descendants = main_menu.get_descendants_by_user(request.user)
        if not section or not descendants:
            return ''  # renders nothing
        return self.render_block(request, template_name='core/block_menu.html',
                                 block_title=ugettext('Menu'),
                                 context={'section': section,
                                          'menu': main_menu,
                                          'descendants': descendants,
                                          'max_num_level': self.get_max_level(),
                                          'max_num_items': self.get_max_num_items()})


class NavigationBlock(BaseMenuBlock, Block):
    name = 'navigation'
    default_place = 'leftsidebar'
    help_text = _('Renders the Navigation')
    verbose_name = _('Navigation Block')
    default_caching_params = {
        'enabled': False,
        'only_anonymous': True,
        'vary_on_user': False,
        'timeout': 3600,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def render(self, request, place, context, *args, **kwargs):
        sections = BaseSection.objects.published()
        section = get_section(request, context)
        if not sections:
            return ''  # renders nothing
        return self.render_block(request, template_name='core/block_navigation.html',
                                 block_title=ugettext('Navigation'),
                                 context={'sections': sections,
                                          'active_section': section,
                                          'max_num_level': self.get_max_level()})


class PortalMenuBlock(BaseSingleMenuBlock, Block):
    name = 'portalmenu'
    default_place = 'header'
    help_text = _('Renders the Portal Menu')
    verbose_name = _('Portal Menu Block')

    def render(self, request, place, context, *args, **kwargs):
        portal_menu = Menu.objects.get(slug=settings.MENU_PORTAL_SLUG)
        return self.render_block(request, template_name='core/block_portal_menu.html',
                                 block_title=ugettext('Portal Menu'),
                                 context={'portal_menu': portal_menu,
                                          'max_num_level': self.get_max_level(),
                                          'max_num_items': self.get_max_num_items()})


class LinkBaseBlock(Block):
    """ Abstract base class for blocks that render portal links """
    category = None
    template_name = 'core/block_portallinks.html'
    help_text = _('Abstract block that render portal links')
    verbose_name = _('Link Base Block')
    default_caching_params = {
        'enabled': False,
        'only_anonymous': False,
        'vary_on_user': True,
        'timeout': 3600,
        'vary_on_url': False,
        'vary_on_language': True,
    }

    def render(self, request, place, context, *args, **kwargs):
        links = PortalLink.objects.filter(category=self.category).visible_by_user(request.user)
        return self.render_block(request, template_name=self.template_name,
                                block_title=ugettext('Portal links'),
                                context={'links': links,
                                         'category': self.category})


class PortalLinksBlock(LinkBaseBlock):
    """Generic block that renders portal links"""
    name = 'portallinks'
    default_place = 'header'
    help_text = _('Generic block that renders portal links')
    verbose_name = _('Portal Links Block')

    config_params = BaseBlock.config_params + [
        params.Single(
            name="category",
            label=_("Portal link category"),
            choices=settings.PORTAL_LINK_CATEGORIES,
            default=settings.PORTAL_LINK_CATEGORIES[0][0],
        ),
    ]

    @property
    def category(self):
        return self.get_config().get('category', None).get_value()

    @property
    def template_name(self):
        category = self.get_config().get('category', None).get_value()
        return 'core/block_%slinks.html' % category


class ContactInfoBlock(ContentBlock):
    """ Block that renders basic contact info of the content """
    name = 'contactinfo'
    default_place = 'aftercontent'
    help_text = _('Block with contact info')
    verbose_name = _('Contact Info block')
    default_caching_params = {
        'enabled': False,
        'only_anonymous': True,
        'vary_on_user': False,
        'timeout': 3600,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def render(self, request, place, content, context, *args, **kwargs):
        return self.render_block(
            request, template_name='core/block_contact_info.html',
            block_title=ugettext('Contact info'),
            context={'contact_info': content.contact_info})


class AnnouncementsBlock(ContentBlock):
    """ Block that displays the site announcements """
    name = 'announcements'
    default_place = 'header'
    help_text = _('Block with the site announcements')
    verbose_name = _('Announcements block')

    def render(self, request, place, content, context, *args, **kwargs):
        announcements = current_announcements_for_request(request, site_wide=True)
        if not announcements:
            return ''

        return self.render_block(
            request, template_name='core/block_announcements.html',
            block_title=ugettext('Announcements'),
            context={'site_wide_announcements': announcements})
