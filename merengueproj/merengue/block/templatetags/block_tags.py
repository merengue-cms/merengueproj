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

from django import template
from django.conf import settings

from merengue.base.models import BaseContent
from merengue.section.models import Section
from merengue.block.blocks import Block, ContentBlock, SectionBlock
from merengue.block.models import RegisteredBlock


register = template.Library()


class RenderBlocksNode(template.Node):

    def __init__(self, place, obj, block_type='block'):
        self.place = place
        self.obj = obj
        self.block_type = block_type

    def render(self, context):
        request = context.get('request', None)
        try:
            obj = None
            if self.obj is not None:
                obj = self.obj.resolve(context)
            rendered_blocks = []
            registered_blocks = RegisteredBlock.objects.actives(ordered=True)
            for registered_block in registered_blocks:
                if registered_block.print_block(self.place):
                    block = registered_block.get_registry_item_class()
                    if self.block_type == 'block' and issubclass(block, Block):
                        rendered_blocks.append(block.render(request,
                                                            self.place,
                                                            context))
                    elif self.block_type == 'contentblock' and issubclass(block, ContentBlock) and isinstance(obj, BaseContent):
                        rendered_blocks.append(block.render(request,
                                                            self.place,
                                                            obj,
                                                            context))
                    elif self.block_type == 'sectionblock' and issubclass(block, SectionBlock) and isinstance(obj, Section):
                        rendered_blocks.append(block.render(request,
                                                            self.place,
                                                            obj,
                                                            context))
            return "<div class='blockContainer %ss'>%s" \
                   "<input type=\"hidden\" class=\"blockPlace\" value=\"%s\">" \
                   "</div>" \
                   % (self.block_type, '\n'.join(rendered_blocks), self.place)
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_blocks')
def do_render_blocks(parser, token, block_type='block'):
    """
    Usage::
      render_blocks "leftsidebar"
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) != 2 and block_type == 'block':
        raise template.TemplateSyntaxError('"%r" tag requires only two '
                                           'arguments' % tag_name)
    if len(bits) != 4 and block_type != 'block':
        raise template.TemplateSyntaxError('"%r" tag requires at four '
                                           'arguments' % tag_name)
    if len(bits) == 4 and bits[2] != 'for':
        raise template.TemplateSyntaxError('"%r" statements should use the '
                                           'format %r "leftsidebar" for '
                                           'obj' % (tag_name, tag_name))
    place = bits[1]
    if len(bits) == 2:
        obj = None
    else:
        obj = parser.compile_filter(bits[3])
    if not (place[0] == place[-1] and place[0] in ('"', "'")):
        raise (template.TemplateSyntaxError, "%r tag's argument should be in "
                                             "quotes" % tag_name)
    return RenderBlocksNode(place[1:-1], obj, block_type)


@register.tag(name='render_content_blocks')
def do_render_content_blocks(parser, token):
    """
    Usage::
      render_content_blocks "rightsidebar" for content
    """
    return do_render_blocks(parser, token, 'contentblock')


@register.tag(name='render_section_blocks')
def do_render_section_blocks(parser, token):
    """
    Usage::
      render_section_blocks "rightsidebar" for section
    """
    return do_render_blocks(parser, token, 'sectionblock')


@register.inclusion_tag('blocks/header.html', takes_context=True)
def render_blocks_media(context):
    return {'request': context.get('request'),
            'MEDIA_URL': settings.MEDIA_URL,
            'content': context.get('content'),
            }
