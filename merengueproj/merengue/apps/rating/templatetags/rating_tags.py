# Copyright (c) 2009 by Yaco Sistemas S.L.
# Contact info: Lorenzo Gil Sanchez <lgs@yaco.es>
#
# This file is part of rating
#
# rating is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rating is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with rating.  If not, see <http://www.gnu.org/licenses/>.

from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import select_template
from django.utils.translation import ugettext as _

from rating.models import Vote, get_vote_choices, get_star_img_width

register = template.Library()


def get_score_info(vote):
    star_img_width = get_star_img_width()

    current_score = vote['score']
    current_rating_width = star_img_width * current_score

    stars = [v[0] for v in get_vote_choices()]

    return {
        'num_votes': vote['num_votes'],
        'current_rating_width': current_rating_width,
        'current_score': current_score,
        'stars': stars,
        'num_stars': len(stars),
        }


class RatingNode(template.Node):

    def __init__(self, obj_variable, readonly=False):
        self.obj_variable = obj_variable
        self.readonly = readonly

    def render(self, context):
        obj = template.resolve_variable(self.obj_variable, context)
        score_info = get_score_info(Vote.objects.get_score(obj))

        # Get the content_type
        app = obj._meta.app_label
        module = obj._meta.module_name
        content_type = ContentType.objects.get(app_label=app, model=module)

        # Allow template overriding
        template_list = (
            'rating/%s/%s/form.html' % (app, module),
            'rating/%s/form.html' % app,
            'rating/form.html',
            'form.html',
            )
        t = select_template(template_list)

        can_vote = False
        if not self.readonly:
            user = context.get('user', None)
            if user is not None:
                can_vote = user.is_authenticated()

        c = template.Context({'can_vote': can_vote,
                              'obj_id': obj.id,
                              'content_type_id': content_type.id,
                              'score_info': score_info,
                              'readonly': self.readonly,
                              })
        c.update(context)
        return t.render(c)


@register.tag
def ratingform(parser, token):
    bits = token.contents.split()
    if len(bits) not in (2, 3):
        raise template.TemplateSyntaxError("'%s' takes one or two arguments"
                                           % bits[0])
    obj_variable = bits[1]

    readonly = False
    if len(bits) == 3:
        if bits[2] == 'readonly':
            readonly = True
        else:
            raise template.TemplateSyntaxError("The second argument must be"
                                               " 'readonly' if present")

    return RatingNode(obj_variable, readonly)


def ratingmedia(context):
    return {'readonly': False,
            'thanks': _(u'Thanks for rating '),
            'MEDIA_URL': context.get('MEDIA_URL', '')}
register.inclusion_tag("ratingmedia.html", takes_context=True)(ratingmedia)


def ratingmediareadonly(context):
    return {'readonly': True,
            'thanks': _(u'Thanks for rating '),
            'MEDIA_URL': context.get('MEDIA_URL', '')}
register.inclusion_tag("ratingmedia.html", takes_context=True)(ratingmediareadonly)
