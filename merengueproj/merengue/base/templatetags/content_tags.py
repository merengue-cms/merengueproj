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
from django.utils.text import unescape_entities


register = template.Library()


@register.inclusion_tag('base/content_title.html', takes_context=True)
def content_title(context, content):
    return {'content': content, 'request': context.get('request')}


@register.inclusion_tag('content_admin_action.html', takes_context=True)
def content_admin_action(context, content):
    user = context.get('request').user
    if hasattr(content, 'can_edit') and callable(content.can_edit):
        can_edit = content.can_edit(user)
    else:
        can_edit = user.is_superuser or user.has_perm(
            content._meta.app_label + '.' + content._meta.get_change_permission())
    return {
        'content': content,
        'user': user,
        'can_edit': can_edit,
        'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
        'THEME_URL': context.get('THEME_URL'),
    }


@register.inclusion_tag('base/content_list.html', takes_context=True)
def content_list(context, resource_list, with_rating=False):
    return {'resource_list': resource_list,
            'request': context.get('request', None),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
            'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
            'with_rating': with_rating,
            'user': context.get('user', None),
             }


@register.inclusion_tag('base/content_thumbnail.html', takes_context=True)
def content_thumbnail(context, content, no_link=False):
    return {'content': content,
            'request': context.get('request', None),
            'no_link': no_link,
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


@register.inclusion_tag('base/content_related_items.html', takes_context=True)
def content_related_items(context, content):
    related_items_excluded = ['story']
    related_items = content.related_items.published().exclude(class_name__in=related_items_excluded)
    related_stories = content.related_items.published().filter(class_name='story')
    related_sections = content.sections.all()

    return {'content': content,
            'related_items': related_items,
            'related_stories': related_stories,
            'related_sections': related_sections,
            'request': context.get('request', None),
            'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


@register.inclusion_tag('base/photo_slide.html', takes_context=True)
def photo_slide(context, contents, slide_id='photo_slide', visible=6, parent_content=None):
    return {'contents': contents,
            'visible': visible,
            'slide_id': slide_id,
            'parent_content': parent_content,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
           }


@register.inclusion_tag('base/video_slide.html', takes_context=True)
def video_slide(context, contents, parent_content=None):
    return {'contents': contents,
            'parent_content': parent_content,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
           }


@register.inclusion_tag('base/image3d_slide.html', takes_context=True)
def image3d_slide(context, contents, parent_content=None):
    return {'contents': contents,
            'parent_content': parent_content,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
           }


@register.inclusion_tag('base/panoramic_slide.html', takes_context=True)
def panoramic_slide(context, contents, size='100x100', parent_content=None):
    return {'contents': contents,
            'parent_content': parent_content,
            'size': size,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
           }


class CuttedNode(template.Node):

    def __init__(self, length, content_node):
        self.content_node = content_node
        self.length = length

    def render(self, context):
        length = self.length
        full_value = self.content_node.render(context)
        value = unescape_entities(full_value)
        if len(value) > length - 3:
            value = value[:length - 3] + '...'
        return '<span title="%s">%s</span>' % (full_value, value)


def cutrender(parser, token):
    bits = list(token.split_contents())
    if len(bits) == 1:
        length = 53
    elif len(bits) != 2:
        raise template.TemplateSyntaxError, '%r takes one argument' % bits[0]
    else:
        length = int(bits[1])
    end_tag = 'end' + bits[0]
    node_content = parser.parse((end_tag, ))
    token = parser.next_token()
    return CuttedNode(length, node_content)
cutrender = register.tag(cutrender)


@register.inclusion_tag('base/cut_objects_list.html', takes_context=True)
def cut_objects_list(context, items, max_len=90, separator=', '):
    cad = ''
    count = 0
    too_long = False
    for item in items:
        if len(cad + item.name) < max_len:
            cad += item.name + separator
            count += 1
        else:
            too_long = True
            break

    return {
        'items': items[:count],
        'too_long': too_long,
    }


@register.filter
def verbose_base_content_name(value, arg=None):
    return value.get_real_instance()._meta.verbose_name


@register.filter
def real_instance(value, arg=None):
    return value.get_real_instance()
