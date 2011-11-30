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
from django.conf import settings
from django.template.loader import render_to_string

from merengue.block.blocks import ContentBlock, SectionBlock
from merengue.block.models import RegisteredBlock, PLACES_DICT
from merengue.block.utils import get_all_blocks_to_display
from merengue.registry import register as merengue_register, get_items_by_name


register = template.Library()


class RenderBlocksNode(template.Node):

    def __init__(self, place, obj, block_type='block', nondraggable=False, noncontained=False):
        self.place = place
        self.obj = obj
        self.block_type = block_type
        self.nondraggable = nondraggable
        self.noncontained = noncontained

    def render(self, context):
        request = context.get('request', None)
        try:
            obj = None
            section = None
            if self.obj is not None:
                if self.block_type == 'contentblock':
                    obj = self.obj.resolve(context)
                elif self.block_type == 'sectionblock':
                    section = self.obj.resolve(context)
            blocks = RegisteredBlock.objects.actives().filter(content=obj)
            return _render_blocks(request, blocks, obj, section, self.place, self.block_type, self.nondraggable, context, self.noncontained)
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_blocks')
def do_render_blocks(parser, token, block_type='block'):
    """
    Usage::
      {% render_blocks "leftsidebar" [nondraggable|noncontained] %}
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) < 2 or (len(bits) > 3 and block_type == 'block'):
        raise template.TemplateSyntaxError('"%r" tag requires two '
                                           'arguments' % tag_name)
    if len(bits) == 3 and (bits[2] != 'nondraggable' and bits[2] != 'noncontained'):
        raise template.TemplateSyntaxError('"%r" invalid argument'
                                           'for tag' % tag_name)
    if (len(bits) != 4 and len(bits) != 5) and block_type != 'block':
        raise template.TemplateSyntaxError('"%r" tag requires at least four '
                                           'arguments' % tag_name)
    if (len(bits) == 4 and bits[2] != 'for') or \
    (len(bits) == 5 and (bits[4] != 'nondraggable' and bits[4] != 'noncontained')):
        raise template.TemplateSyntaxError('"%r" statements should use the '
                                           'format %r "leftsidebar" for '
                                           'obj [nondraggable|noncontained]' % (tag_name, tag_name))
    place = bits[1]
    if len(bits) == 2 or len(bits) == 3:
        obj = None
    else:
        obj = parser.compile_filter(bits[3])
    nondraggable = False
    noncontained = False
    if len(bits) == 3:
        nondraggable = bits[2] == 'nondraggable'
        noncontained = bits[2] == 'noncontained'
    elif len(bits) == 5:
        nondraggable = bits[4] == 'nondraggable'
        noncontained = bits[4] == 'noncontained'

    if not (place[0] == place[-1] and place[0] in ('"', "'")):
        raise (template.TemplateSyntaxError, "%r tag's argument should be in "
                                             "quotes" % tag_name)
    return RenderBlocksNode(place[1:-1], obj, block_type, nondraggable, noncontained)


@register.tag(name='render_content_blocks')
def do_render_content_blocks(parser, token):
    """
    Usage::
      {% render_content_blocks "rightsidebar" for content [nondraggable|noncontained] %}
    """
    return do_render_blocks(parser, token, 'contentblock')


@register.tag(name='render_section_blocks')
def do_render_section_blocks(parser, token):
    """
    Usage::
      {% render_section_blocks "rightsidebar" for section [nondraggable|noncontained] %}
    """
    return do_render_blocks(parser, token, 'sectionblock')


def _print_block(block, place, block_type, request):
    return block.get_registered_item().print_block(place, request.get_full_path())


def _render_blocks(request, blocks, obj, section, place, block_type, nondraggable, context, noncontained=False):
    rendered_blocks = []
    for block in blocks.get_items():
        if ((isinstance(block, ContentBlock) and not obj) or
            (isinstance(block, SectionBlock) and not section) or
            not _print_block(block, place, block_type, request)):
            continue
        # building render method arguments
        render_args = [request, place]
        if isinstance(block, ContentBlock):
            render_args.append(obj)
        elif isinstance(block, SectionBlock):
            render_args.append(section)
        render_args.append(context)
        # append the block rendering to list
        rendered_blocks.append(block.get_rendered_content(request, render_args))
    if noncontained:
        wrapped_blocks = ['%s' % s for s in rendered_blocks]
    else:
        wrapped_blocks = ['<div class="blockWrapper">%s</div>' % s for s in rendered_blocks]

    return render_to_string('blocks/block_container.html',
                            {'block_type': block_type,
                             'nondraggable': nondraggable,
                             'noncontained': noncontained,
                             'blocks': '\n'.join(wrapped_blocks),
                             'content': context.get('content', None),
                             'section': context.get('section', None),
                             'place': place,
                             'place_title': PLACES_DICT.get(place, place),
                            })


class RenderAllBlocksNode(template.Node):

    def __init__(self, place, nondraggable=False, noncontained=False):
        self.place = place
        self.nondraggable = nondraggable
        self.noncontained = noncontained

    def render(self, context):
        """
        Three block groups are fetched separately and rendered in increasing priority:
            - site blocks (no content)
            - section related blocks
            - content related blocks
        """
        request = context.get('request', None)
        try:
            content = context.get('content', None)
            section = context.get('section', None)
            blocks = get_all_blocks_to_display(self.place, content, section)
            result = _render_blocks(request, blocks, content, section, self.place, "block", self.nondraggable, context, self.noncontained)
            return result
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_all_blocks')
def do_render_all_blocks(parser, token):
    """
    It's a tag like using all render_*_blocks.

    Usage::
      {% render_all_blocks "leftsidebar" [nondraggable|noncontained] %}

    Last templatetag call is a shortcut to this logic::

        {% render_blocks "leftsidebar" [nondraggable|noncontained] %}
        {% if content %}
            {% render_content_blocks "leftsidebar" for content [nondraggable|noncontained] %}
        {% endif %}
        {% if section %}
            {% render_section_blocks "leftsidebar" for section [nondraggable|noncontained] %}
        {% endif %}
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) < 2:
        raise template.TemplateSyntaxError('"%r" tag requires at least '
                                           'two arguments' % tag_name)
    if len(bits) > 3 or (len(bits) == 3 and (bits[2] != 'nondraggable' and bits[2] != 'noncontained')):
        raise template.TemplateSyntaxError('"%r" tag requires format '
                                           'render_all_blocks "leftsidebar" '
                                           '[nondraggable|noncontained]' % tag_name)
    place = bits[1]
    if not (place[0] == place[-1] and place[0] in ('"', "'")):
        raise (template.TemplateSyntaxError, "%r tag's argument should be in "
                                             "quotes" % tag_name)
    nondraggable = False
    noncontained = False
    if len(bits) == 3:
        nondraggable = bits[2] == 'nondraggable'
        noncontained = bits[2] == 'noncontained'
    return RenderAllBlocksNode(place[1:-1], nondraggable, noncontained)


class RenderSingleBlockNode(template.Node):

    def __init__(self, block):
        self.block = block

    def render(self, context):
        request = context.get('request', None)
        block = self.block
        if not block:
            return ''
        try:
            content = context.get('content', None)
            section = context.get('section', None)
            place = ''
            render_args = [request, place]
            if isinstance(block, ContentBlock):
                render_args.append(content)
            elif isinstance(block, SectionBlock):
                render_args.append(section)
            render_args.append(context)
            return block.get_rendered_content(request, render_args)
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_single_block')
def do_render_single_block(parser, token):
    """
    Usage::
      {% render_single_block "plugins.news.blocks.NewsBlock" "news_block" %}
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) != 3:
        raise template.TemplateSyntaxError('"%r" tag requires two '
                                           'arguments' % tag_name)
    splitted_block_name = bits[1][1:-1].split('.')
    block_name = bits[2][1:-1]
    module = '.'.join(splitted_block_name[:-1])
    classname = splitted_block_name[-1]
    blocks = RegisteredBlock.objects.filter(module=module,
                                            class_name=classname,
                                            name=block_name)
    if blocks:
        block = blocks[0].get_registry_item()
    else:
        try:
            old_block = get_items_by_name('%s.%s' % (module, classname)).next()
            reg_block = merengue_register(old_block.__class__)
            reg_block.active = reg_block.is_fixed = False
            reg_block.name = block_name
            reg_block.save()
            block = reg_block.get_registry_item()
        except RegisteredBlock.DoesNotExist:
            block = None
    return RenderSingleBlockNode(block)


@register.inclusion_tag('blocks/header.html', takes_context=True)
def render_blocks_media(context):
    return {'request': context.get('request'),
            'MEDIA_URL': settings.MEDIA_URL,
            'content': context.get('content'),
            }
