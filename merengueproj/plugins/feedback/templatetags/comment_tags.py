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
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from merengue.pluggable.utils import get_plugin
from plugins.feedback.forms import CaptchaFreeThreadedCommentForm
from threadedcomments.models import FreeThreadedComment


register = template.Library()


@register.inclusion_tag('feedback/content_comments.html', takes_context=True)
def content_comments(context, content):
    # first level of comments
    content_type = ContentType.objects.get_for_model(content)
    is_moderated = (context['request'] and context['request'].user and context['request'].user.is_staff)
    if is_moderated:
        comments = FreeThreadedComment.objects.all_for_object(content_object=content, parent__isnull=True).order_by('date_submitted')
    else:
        comments = FreeThreadedComment.public.all_for_object(content_object=content, parent__isnull=True).order_by('date_submitted')
    plugin_config = get_plugin('feedback').get_config()
    number_of_comments = plugin_config.get('number_of_comments').get_value()
    show_children = plugin_config.get('show_children').get_value()
    show_links = plugin_config.get('show_links').get_value()
    has_pagination = number_of_comments > 0
    return {'content': content,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'comments': comments,
            'content_type_id': content_type.id,
            'form': context.get('form', None),
            'number_of_comments': number_of_comments,
            'has_pagination': has_pagination,
            'show_children': show_children,
            'show_links': show_links,
           }


@register.inclusion_tag('feedback/content_comment.html', takes_context=True)
def content_comment(context, content, comment, show_links=True, show_children=False):
    content_type = ContentType.objects.get_for_model(content)
    is_moderated = (context['request'] and context['request'].user and context['request'].user.is_staff)
    if show_children:
        children_comments = comment.children.all().order_by('date_submitted')
        if not is_moderated:
            children_comments = FreeThreadedComment.public.filter(Q(id__in=comment.children.all().values('id').query))
    else:
        children_comments = []

    censured = not comment.is_public

    return {'content': content,
            'comment': comment,
            'censured': censured,
            'is_moderated': is_moderated,
            'content_type_id': content_type.id,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'show_children': show_children,
            'children_comments': children_comments,
            'show_links': show_links,
           }


@register.inclusion_tag('feedback/content_comment_add.html', takes_context=True)
def content_comment_add_form(context, content, parent_id=None):
    form = context.get('form', None)
    if not form or form.content._get_real_instance() != content:
        form = CaptchaFreeThreadedCommentForm(context['request'].user)
        form.content = content
    request = context['request']
    if request.user:
        form.initial = {'name': request.user.username}
    content_type = ContentType.objects.get_for_model(content)
    return {'content_id': content.id,
            'content_type_id': content_type.id,
            'parent_id': parent_id,
            'form': form,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
           }


@register.inclusion_tag('feedback/comments_media.html', takes_context=True)
def comments_media(context):
    return {'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
           }


@register.simple_tag
def comment_admin_link(comment):
    link = '/admin/%s/%s/%d/%s' % (comment._meta.app_label,
                                    comment._meta.module_name, comment.id, '')
    return link
