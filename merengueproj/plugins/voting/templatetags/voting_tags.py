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
