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

from plugins.voting.models import Vote, get_vote_choices, DEFAULT_STAR_IMG_WIDTH
from plugins.voting.utils import get_can_vote
register = template.Library()


def voting(context, content, readonly=False):
    try:
        vote = content.vote_set.get()
        vote_value = vote.vote * DEFAULT_STAR_IMG_WIDTH
    except Vote.DoesNotExist:
        vote = None
        vote_value = 0
    return {'content': content,
            'vote': vote,
            'vote_value': vote_value,
            'stars': get_vote_choices(),
            'user': context.get('user'),
            'can_vote': get_can_vote(content, context.get('user')),
            'readonly': readonly,
          }
register.inclusion_tag("voting/voting_form.html", takes_context=True)(voting)
