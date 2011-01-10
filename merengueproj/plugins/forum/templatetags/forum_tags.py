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

from merengue.perms.utils import has_permission

register = template.Library()


@register.inclusion_tag('forum/thread_comment.html', takes_context=True)
def thread_comment(context, comment):
    is_moderated = context['request'] and\
                   context['request'].user and\
                   (context['request'].user.is_superuser or has_permission(comment.thread.forum, context['request'].user, 'moderate_forum'))
    is_auth = (context['request'] and context['request'].user and context['request'].user.is_authenticated())
    children_comments = comment.children.all().order_by('date_submitted')
    if not is_moderated:
        children_comments = children_comments.filter(banned=False)

    return {'thread': comment.thread,
            'comment': comment,
            'is_moderated': is_moderated,
            'actions': (is_moderated or not comment.thread.closed) and is_auth,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'children_comments': children_comments,
           }
