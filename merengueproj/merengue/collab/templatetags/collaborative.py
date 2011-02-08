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
from django.contrib.contenttypes.models import ContentType

from cmsutils.forms.widgets import TINYMCE_JS
from merengue.collab.utils import get_comments_for_object


register = template.Library()


def collaborative_comments_media(context):
    return {
        'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
        'user': context.get('user', None),
        'request': context['request'],
    }
register.inclusion_tag("collab/collaborative_comments_media.html", takes_context=True)(collaborative_comments_media)


def collaborative_comments(context, content):
    comments = get_comments_for_object(content)
    return {'num_comments': comments.count(),
            'ct': ContentType.objects.get_for_model(content),
            'content': content,
            }
register.inclusion_tag("collab/collaborative_comments.html", takes_context=True)(collaborative_comments)


def collaborative_translation_media(context):
    return {
        'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
        'TINYMCE_JS': TINYMCE_JS,
        'user': context.get('user', None),
        'request': context['request'],
    }
register.inclusion_tag("collab/collaborative_translation_media.html", takes_context=True)(collaborative_translation_media)


def collaborative_translation(context, content, field, is_html=False):
    return {'content': content,
            'ct': ContentType.objects.get_for_model(content),
            'field': field,
            'is_html': bool(is_html),
            }
register.inclusion_tag("collab/collaborative_translation.html", takes_context=True)(collaborative_translation)


class IfNode(template.Node):

    def __init__(self, if_node, else_node):
        self.if_node = if_node
        self.else_node = else_node

    def __repr__(self):
        return '<IfNode>'

    def check(self, context):
        raise NotImplementedError

    def render(self, context):
        if self.check(context):
            return self.if_node.render(context)
        else:
            return self.else_node.render(context)


class IsVisibleCommentNode(IfNode):

    def __init__(self, comment, *args):
        self.comment = comment
        super(IsVisibleCommentNode, self).__init__(*args)

    def check(self, context):
        comment = template.Variable(self.comment).resolve(context)
        user = template.Variable('user').resolve(context)
        status = comment.get_last_revision_status()
        if user.has_perm('can_revise') or not status\
           or not status.type.result == 'hide':
            return True
        else:
            return False


class IsVisibleStatusNode(IfNode):

    def __init__(self, status, *args):
        self.status = status
        super(IsVisibleStatusNode, self).__init__(*args)

    def check(self, context):
        status = template.Variable(self.status).resolve(context)
        user = template.Variable('user').resolve(context)
        if user.has_perm('can_revise') \
           or not status.type.result == 'hide':
            return True
        else:
            return False


def ifcanviewcollabcomment(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 2:
        raise template.TemplateSyntaxError('%r takes one arguments' % bits[0])
    comment = bits[1]
    end_tag = 'end' + bits[0]
    node_ismember = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        node_notismember = parser.parse((end_tag, ))
        parser.delete_first_token()
    else:
        node_notismember = template.NodeList()
    return IsVisibleCommentNode(comment, node_ismember, node_notismember)
ifcanviewcollabcomment = register.tag(ifcanviewcollabcomment)


def ifcanviewstatus(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 2:
        raise template.TemplateSyntaxError('%r takes one arguments' % bits[0])
    status = bits[1]
    end_tag = 'end' + bits[0]
    node_ismember = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        node_notismember = parser.parse((end_tag, ))
        parser.delete_first_token()
    else:
        node_notismember = template.NodeList()
    return IsVisibleStatusNode(status, node_ismember, node_notismember)
ifcanviewstatus = register.tag(ifcanviewstatus)
