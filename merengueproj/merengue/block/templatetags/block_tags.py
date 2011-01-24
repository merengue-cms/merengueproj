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

from django import template
from django.db.models import Q
from django.conf import settings

from merengue.base.models import BaseContent
from merengue.section.models import Section
from merengue.block.blocks import Block, ContentBlock, SectionBlock
from merengue.block.models import RegisteredBlock, BlockContentRelation


register = template.Library()


def _render_blocks_queryset(blocks, request, obj, place, block_type, context):
    rendered_blocks = []
    for registered_block in blocks:
        block_content_relation = registered_block.get_content_related_block(
           obj, place)
        if registered_block.print_block(place, request.get_full_path()) or \
                block_content_relation:
            block = registered_block.get_registry_item_class()
            if block_type == 'block' and issubclass(block, Block):
                rendered_blocks.append(block.render(request,
                                                    place,
                                                    context,
                                                    block_content_relation))
            elif block_type == 'contentblock' and issubclass(block, ContentBlock) and isinstance(obj, BaseContent):
                rendered_blocks.append(block.render(request,
                                                    place,
                                                    obj,
                                                    context,
                                                    block_content_relation))
            elif block_type == 'sectionblock' and issubclass(block, SectionBlock) and isinstance(obj, Section):
                rendered_blocks.append(block.render(request,
                                                    place,
                                                    obj,
                                                    context,
                                                    block_content_relation))
    return rendered_blocks


def _render_blocks(request, obj, place, block_type, context):
    rendered_blocks = []
    content = context.get('content')
    content_related_blocks = BlockContentRelation.objects.filter(
        content=content)
    filter_filters = Q(placed_at=place) | Q(placed_at='all')
    exclude_filters = Q(blockcontentrelation__in=content_related_blocks.filter(
            placed_at=place, overwrite_if_place=True)) | Q(
        blockcontentrelation__in=content_related_blocks.filter(
                    overwrite_allways=True),
        )
    registered_blocks = RegisteredBlock.objects.exclude(exclude_filters).filter(
        filter_filters).actives(ordered=True)
    static_content_blocks = RegisteredBlock.objects.filter(
        blockcontentrelation__in=BlockContentRelation.objects.filter(
            content=content, placed_at=place))

    # first we get the rendered blocks of those that are "generic"
    rendered_blocks = _render_blocks_queryset(registered_blocks, request, obj,
                                              place, block_type, context)
    # then we get the blocks related with the content
    rendered_blocks += _render_blocks_queryset(static_content_blocks, request,
                                               content, place, block_type, context)

    return "<div class='blockContainer %ss'>%s" \
            "<input type=\"hidden\" class=\"blockPlace\" value=\"%s\">" \
            "</div>" \
            % (block_type, '\n'.join(rendered_blocks), place)


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
            return _render_blocks(request, obj, self.place, self.block_type, context)
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_blocks')
def do_render_blocks(parser, token, block_type='block'):
    """
    Usage::
      {% render_blocks "leftsidebar" %}
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
      {% render_content_blocks "rightsidebar" for content %}
    """
    return do_render_blocks(parser, token, 'contentblock')


@register.tag(name='render_section_blocks')
def do_render_section_blocks(parser, token):
    """
    Usage::
      {% render_section_blocks "rightsidebar" for section %}
    """
    return do_render_blocks(parser, token, 'sectionblock')


class RenderAllBlocksNode(template.Node):

    def __init__(self, place):
        self.place = place

    def render(self, context):
        request = context.get('request', None)
        try:
            content = context.get('content', None)
            section = context.get('section', None)
            result = _render_blocks(request, None, self.place, "block", context)
            if content:
                result += _render_blocks(request, content, self.place, "contentblock", context)
            if section:
                result += _render_blocks(request, section, self.place, "sectionblock", context)
            return result
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_all_blocks')
def do_render_all_blocks(parser, token):
    """
    It's a tag like using all render_*_blocks.

    Usage::
      {% render_all_blocks "leftsidebar" %}

    Last templatetag call is a shortcut to this logic::

        {% render_blocks "leftsidebar" %}
        {% if content %}
            {% render_content_blocks "leftsidebar" for content %}
        {% endif %}
        {% if section %}
            {% render_section_blocks "leftsidebar" for section %}
        {% endif %}
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) != 2:
        raise template.TemplateSyntaxError('"%r" tag requires only one '
                                           'argument' % tag_name)
    place = bits[1]
    if not (place[0] == place[-1] and place[0] in ('"', "'")):
        raise (template.TemplateSyntaxError, "%r tag's argument should be in "
                                             "quotes" % tag_name)
    return RenderAllBlocksNode(place[1:-1])


class RenderSingleBlockNode(template.Node):

    def __init__(self, block):
        self.block = block

    def render(self, context):
        request = context.get('request', None)
        if not self.block:
            return ''
        try:
            obj = None
            place = ''
            return self.block.render(request, obj, place, context)
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_single_block')
def do_render_single_block(parser, token):
    """
    Usage::
      {% render_single_block "plugins.news.blocks.NewsBlock" %}
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) != 2:
        raise template.TemplateSyntaxError('"%r" tag requires only two '
                                           'arguments' % tag_name)
    splitted_block_name = bits[1][1:-1].split('.')
    module = '.'.join(splitted_block_name[:-1])
    classname = splitted_block_name[-1]
    try:
        block = RegisteredBlock.objects.get(module=module, class_name=classname).get_registry_item_class()
    except RegisteredBlock.DoesNotExist:
        block = None
    return RenderSingleBlockNode(block)


@register.inclusion_tag('blocks/header.html', takes_context=True)
def render_blocks_media(context):
    return {'request': context.get('request'),
            'MEDIA_URL': settings.MEDIA_URL,
            'content': context.get('content'),
            }
