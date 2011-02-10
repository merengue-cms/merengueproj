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
from django.utils.translation import ugettext as _

from merengue.block.blocks import Block, ContentBlock
from merengue.registry import params
from merengue.section.models import BaseSection, Menu
from merengue.section.utils import get_section
from merengue.portal.models import PortalLink


class BaseMenuBlock(object):

    config_params = [
        params.Integer(name='max_num_level',
                       label=_('maximum number of levels to show'), default=-1)]

    def get_max_level(self):
        max_value = self.get_config().get('max_num_level', None)
        if max_value:
            return max_value.get_value()
        return -1


class CoreMenuBlock(BaseMenuBlock, Block):
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
            descendants = main_menu.get_descendants()
        if not section or not descendants:
            return ''  # renders nothing
        return self.render_block(request, template_name='core/block_menu.html',
                                 block_title=_('Menu'),
                                 context={'section': section,
                                          'menu': main_menu,
                                          'descendants': descendants,
                                          'max_num_level': self.get_max_level()})


class NavigationBlock(BaseMenuBlock, Block):
    name = 'navigation'
    default_place = 'leftsidebar'
    help_text = _('Renders the Navigation')
    verbose_name = _('Navigation Block')

    def render(self, request, place, context, *args, **kwargs):
        sections = BaseSection.objects.published()
        section = get_section(request, context)
        if not sections:
            return ''  # renders nothing
        return self.render_block(request, template_name='core/block_navigation.html',
                                 block_title=_('Navigation'),
                                 context={'sections': sections,
                                          'active_section': section,
                                          'max_num_level': self.get_max_level()})


class PortalMenuBlock(BaseMenuBlock, Block):
    name = 'portalmenu'
    default_place = 'header'
    help_text = _('Renders the Portal Menu')
    verbose_name = _('Portal Menu Block')

    def render(self, request, place, context, *args, **kwargs):
        portal_menu = Menu.objects.get(slug=settings.MENU_PORTAL_SLUG)
        return self.render_block(request, template_name='core/block_portal_menu.html',
                                 block_title=_('Portal Menu'),
                                 context={'portal_menu': portal_menu,
                                         'max_num_level': self.get_max_level()})


class LinkBaseBlock(Block):
    """ Abstract base class for blocks that render portal links """
    category = None
    template_name = 'core/block_portallinks.html'
    help_text = _('Abstract block that render portal links')
    verbose_name = _('Link Base Block')

    def render(self, request, place, context, *args, **kwargs):
        links = PortalLink.objects.filter(category=self.category)
        return self.render_block(request, template_name=self.template_name,
                                block_title=_('Portal links'),
                                context={'links': links,
                                         'category': self.category})


class PrimaryLinksBlock(LinkBaseBlock):
    """ Block that renders primary portal links """
    name = 'primarylinks'
    default_place = 'header'
    category = 'primary'
    template_name = 'core/block_primarylinks.html'
    help_text = _('Block reporesents the Primary Links')
    verbose_name = _('Primary Links Block')


class SecondaryLinksBlock(LinkBaseBlock):
    """ Block that renders secondary portal links """
    name = 'secondarylinks'
    default_place = 'footer'
    category = 'secondary'
    template_name = 'core/block_secondarylinks.html'
    help_text = _('Block that renders secondary portal links')
    verbose_name = _('Link Base Block')


class ContactInfoBlock(ContentBlock):
    """ Block that renders basic contact info of the content """
    name = 'contactinfo'
    default_place = 'aftercontent'
    help_text = _('Block with contact info')
    verbose_name = _('Contact Info block')

    def render(self, request, place, content, context, *args, **kwargs):
        return self.render_block(
            request, template_name='core/block_contact_info.html',
            block_title=_('Contact info'),
            context={'contact_info': content.contact_info})
