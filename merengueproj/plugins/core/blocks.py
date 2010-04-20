from django.conf import settings
from django.utils.translation import ugettext as _

from merengue.block.blocks import Block
from merengue.section.models import BaseSection, Menu
from merengue.portal.models import PortalLink


class CoreMenuBlock(Block):
    name = 'coremenu'
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request, place):
        if not request.section:
            return '' # renders nothing
        return cls.render_block(request, template_name='core/block_menu.html',
                                block_title=_('Menu'),
                                context={'section': request.section})


class NavigationBlock(Block):
    name = 'navigation'
    default_place = 'footer'

    @classmethod
    def render(cls, request, place):
        sections = BaseSection.objects.published()
        return cls.render_block(request, template_name='core/block_navigation.html',
                                block_title=_('Menu'),
                                context={'sections': sections,
                                         'active_section': request.section})


class PortalMenuBlock(Block):
    name = 'portalmenu'
    default_place = 'beforecontent'

    @classmethod
    def render(cls, request, place):
        portal_menu = Menu.objects.get(id=settings.MENU_PORTAL_ID)
        return cls.render_block(request, template_name='core/block_portal_menu.html',
                                block_title=_('Portal Menu'),
                                context={'portal_menu': portal_menu})


class LinkBaseBlock(Block):
    """ Abstract base class for blocks that render portal links """
    category = None

    @classmethod
    def render(cls, request, place):
        links = PortalLink.objects.filter(category=cls.category)
        return cls.render_block(request, template_name='core/block_portallinks.html',
                                block_title=_('Portal links'),
                                context={'links': links,
                                         'category': cls.category})


class PrimaryLinksBlock(LinkBaseBlock):
    """ Block that renders primary portal links """
    name = 'primarylinks'
    default_place = 'header'
    category = 'primary'


class SecondaryLinksBlock(LinkBaseBlock):
    """ Block that renders secondary portal links """
    name = 'secondarylinks'
    default_place = 'footer'
    category = 'secondary'
