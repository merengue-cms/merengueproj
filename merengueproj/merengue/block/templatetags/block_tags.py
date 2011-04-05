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

from merengue.block.blocks import BaseBlock, ContentBlock, SectionBlock
from merengue.block.models import RegisteredBlock
from merengue.registry import register as merengue_register, get_items_by_name


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
            blocks = RegisteredBlock.objects.actives().filter(content=obj)
            return _render_blocks(request, blocks, obj, self.place, self.block_type, context)
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


def _print_block(block, place, block_type, request):
    if block_type == 'block' and isinstance(block, BaseBlock) or \
       block_type == 'contentblock' and isinstance(block, ContentBlock) or \
       block_type == 'sectionblock' and isinstance(block, SectionBlock) or \
       block.content is not None:  # block related to content is printed always
        return block.get_registered_item().print_block(place, request.get_full_path())
    else:
        return False


def _render_blocks(request, blocks, obj, place, block_type, context):
    rendered_blocks = []
    for block in blocks.get_items():
        if not _print_block(block, place, block_type, request):
            continue
        # building render method arguments
        render_args = [request, place]
        if isinstance(block, ContentBlock) or isinstance(block, SectionBlock):
            render_args.append(obj)
        render_args.append(context)
        # append the block rendering to list
        rendered_blocks.append(block.render(*render_args))

    wrapped_blocks = ['<div class="blockWrapper">%s</div>' % s for s in rendered_blocks]

    return "<div class='blockContainer %ss'>%s" \
            "<input type=\"hidden\" class=\"blockPlace\" value=\"%s\">" \
            "</div>" \
            % (block_type, '\n'.join(wrapped_blocks), place)


def _get_blocks_to_display(place=None, content=None):
    """
    Gets content related blocks excluding the ones overwritten by blocks within the same content
    """
    if content:
        blocks = content.registeredblock_set.all()
    else:
        blocks = RegisteredBlock.objects.actives().filter(content__isnull=True)

    overwrite = Q(placed_at=place, overwrite_if_place=True) | Q(overwrite_always=True)
    excluders = blocks.filter(overwrite)
    excluded = blocks.none()
    for b in excluders:
        excluded |= blocks.filter(~Q(id=b.id), module=b.module, class_name=b.class_name, overwrite_always=False)

    return blocks.exclude(id__in=[b.id for b in excluded])


class RenderAllBlocksNode(template.Node):

    def __init__(self, place):
        self.place = place

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
            overwrite = Q(placed_at=self.place, overwrite_if_place=True) | Q(overwrite_always=True)

            blocks = _get_blocks_to_display()
            if section:
                section_blocks = _get_blocks_to_display(self.place, section)
                for b in section_blocks.filter(overwrite):
                    blocks = blocks.exclude(module=b.module, class_name=b.class_name)
            if content:
                content_blocks = _get_blocks_to_display(self.place, content)
                for b in content_blocks.filter(overwrite):
                    blocks = blocks.exclude(module=b.module, class_name=b.class_name)
                    if section:
                        section_blocks = section_blocks.exclude(module=b.module, class_name=b.class_name)

            result = _render_blocks(request, blocks, content, self.place, "block", context)
            if section:
                result += _render_blocks(request, section_blocks, section, self.place, "sectionblock", context)
            if content:
                result += _render_blocks(request, content_blocks, content, self.place, "contentblock", context)
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
            if not ContentBlock in self.block.__class__.mro() and not SectionBlock in self.block.__class__.mro():
                return self.block.render(request, place, context)
            else:
                return self.block.render(request, obj, place, context)
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
        raise template.TemplateSyntaxError('"%r" tag requires only two '
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
