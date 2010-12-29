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
from django.utils.translation import ugettext as _, ugettext_lazy

from merengue.block.blocks import Block
from merengue.section.models import BaseSection, Menu
from merengue.portal.models import PortalLink


class CoreMenuBlock(Block):
    name = 'coremenu'
    default_place = 'leftsidebar'
    help_text = ugettext_lazy('Renders the Menu')
    verbose_name = ugettext_lazy('Core Menu Block')

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        section = request.section
        if not section:
            return '' # renders nothing
        main_menu = section.main_menu
        descendants = main_menu.get_descendants()
        if not request.section or not descendants:
            return '' # renders nothing
        return cls.render_block(request, template_name='core/block_menu.html',
                                block_title=_('Menu'),
                                context={'section': section,
                                         'menu': main_menu,
                                         'descendants': descendants})


class NavigationBlock(Block):
    name = 'navigation'
    default_place = 'leftsidebar'
    help_text = ugettext_lazy('Renders the Navigation')
    verbose_name = ugettext_lazy('Navigation Block')

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        sections = BaseSection.objects.published()
        if not sections:
            return '' # renders nothing
        return cls.render_block(request, template_name='core/block_navigation.html',
                                block_title=_('Navigation'),
                                context={'sections': sections,
                                         'active_section': request.section})


class PortalMenuBlock(Block):
    name = 'portalmenu'
    default_place = 'header'
    help_text = ugettext_lazy('Renders the Portal Menu')
    verbose_name = ugettext_lazy('Portal Menu Block')

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        portal_menu = Menu.objects.get(slug=settings.MENU_PORTAL_SLUG)
        return cls.render_block(request, template_name='core/block_portal_menu.html',
                                block_title=_('Portal Menu'),
                                context={'portal_menu': portal_menu})


class LinkBaseBlock(Block):
    """ Abstract base class for blocks that render portal links """
    category = None
    template_name = 'core/block_portallinks.html'
    help_text = ugettext_lazy('Abstract block that render portal links')
    verbose_name = ugettext_lazy('Link Base Block')

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        links = PortalLink.objects.filter(category=cls.category)
        return cls.render_block(request, template_name=cls.template_name,
                                block_title=_('Portal links'),
                                context={'links': links,
                                         'category': cls.category})


class PrimaryLinksBlock(LinkBaseBlock):
    """ Block that renders primary portal links """
    name = 'primarylinks'
    default_place = 'header'
    category = 'primary'
    template_name = 'core/block_primarylinks.html'
    help_text = ugettext_lazy('Block reporesents the Primary Links')
    verbose_name = ugettext_lazy('Primary Links Block')


class SecondaryLinksBlock(LinkBaseBlock):
    """ Block that renders secondary portal links """
    name = 'secondarylinks'
    default_place = 'footer'
    category = 'secondary'
    template_name = 'core/block_secondarylinks.html'
    help_text = ugettext_lazy('Block that renders secondary portal links')
    verbose_name = ugettext_lazy('Link Base Block')
