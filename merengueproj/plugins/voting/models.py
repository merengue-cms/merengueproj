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

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


from merengue.base.models import BaseContent

DEFAULT_STARS = (_('Very bad'), _('Bad'), _('OK'), _('Good'), _('Very good'))
DEFAULT_MIN_SCORE = 1
DEFAULT_STAR_IMG_WIDTH = 17


def get_vote_choices():
    stars = getattr(settings, 'RATING_STARS', DEFAULT_STARS)
    return [(i+1, star) for i, star in enumerate(stars)]


def get_min_score():
    return getattr(settings, 'RATING_MIN_SCORE', DEFAULT_MIN_SCORE)


def get_max_score():
    return get_min_score() + len(get_vote_choices()) - 1


class VoteManager(models.Manager):

    def record_vote(self, obj, user, vote):
        """
        Record a user's vote on a given object. Only allows a given user
        to vote once, though that vote may be changed.

        A zero vote indicates that any existing vote should be removed.
        """
        min_score, max_score = get_min_score(), get_max_score()
        if vote not in range(min_score, max_score + 1):
            raise ValueError('Invalid vote (must be minimum %d and maximum %d'
                             % (min_score, max_score))
        try:
            v = self.get(content__pk=obj.pk)
            v.users.add(user)
            v.vote = (float(v.vote * v.num_votes) + vote) / (v.num_votes + 1)
            v.num_votes = v.num_votes + 1
            v.save()
        except Vote.DoesNotExist:
            if vote != 0:
                v = self.create(content=obj,
                                num_votes=1,
                                vote=vote)
                v.users.add(user)


class Vote(models.Model):
    vote = models.FloatField()
    num_votes = models.IntegerField(default=1, editable=False)
    content = models.ForeignKey(BaseContent)
    users = models.ManyToManyField(User,
                                  verbose_name=_('users'),
                                  related_name = 'votes')

    objects = VoteManager()

    def __unicode__(self):
        return u"%s --> %s" % (self.content, self.vote)
