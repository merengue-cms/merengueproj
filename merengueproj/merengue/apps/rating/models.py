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

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import connection, models
from django.utils.translation import ugettext_lazy as _


# customizable setttings (just change DEFAULT by RATING)
DEFAULT_STARS = (_('Very bad'), _('Bad'), _('OK'), _('Good'), _('Very good'))
DEFAULT_STAR_IMG_WIDTH = 17
DEFAULT_MIN_SCORE = 1


def get_vote_choices():
    stars = getattr(settings, 'RATING_STARS', DEFAULT_STARS)
    return [(star, i+1) for i, star in enumerate(stars)]


def get_star_img_width():
    return getattr(settings, 'RATING_STAR_IMG_WIDTH', DEFAULT_STAR_IMG_WIDTH)


def get_min_score():
    return getattr(settings, 'RATING_MIN_SCORE', DEFAULT_MIN_SCORE)


def get_max_score():
    return get_min_score() + len(get_vote_choices()) - 1


class VoteManager(models.Manager):

    def get_score(self, obj):
        """
        Get a dictionary containing the total score for ``obj`` and
        the number of votes it's received.
        """
        query = """
SELECT AVG(vote), COUNT(*)
FROM %s
WHERE content_type_id = %%s
  AND object_id = %%s""" % connection.ops.quote_name(self.model._meta.db_table)
        ctype = ContentType.objects.get_for_model(obj)
        cursor = connection.cursor()
        cursor.execute(query, [ctype.id, obj.id])
        result = cursor.fetchall()[0]
        return {'score': result[0] or 0, 'num_votes': result[1]}

    def get_scores_in_bulk(self, objects):
        """
        Get a dictionary mapping object ids to total score and number
        of votes for each object.
        """
        query = """
SELECT object_id, AVG(vote), COUNT(vote)
FROM %s
WHERE content_type_id = %%s
  AND object_id IN (%s)
GROUP BY object_id""" % (
            connection.ops.quote_name(self.model._meta.db_table),
            ','.join(['%s'] * len(objects)),
        )
        ctype = ContentType.objects.get_for_model(objects[0])
        cursor = connection.cursor()
        cursor.execute(query, [ctype.id] + [obj.id for obj in objects])
        results = cursor.fetchall()
        return dict([(object_id, {
                          'score': score,
                          'num_votes': num_votes,
                      }) for object_id, score, num_votes in results])

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
        ctype = ContentType.objects.get_for_model(obj)
        try:
            v = self.get(user=user, content_type=ctype, object_id=obj.id)
            if vote == 0:
                v.delete()
            else:
                v.vote = vote
                v.save()
        except Vote.DoesNotExist:
            if vote != 0:
                self.create(user=user, content_type=ctype,
                            object_id=obj.id, vote=vote)

    def get_top(self, Model, limit=10, reversed=False):
        """
        Get the top N scored objects for a given model.

        Yields (object, score) tuples.
        """
        ctype = ContentType.objects.get_for_model(Model)
        query = """
SELECT object_id, AVG(vote)
FROM %s
WHERE content_type_id = %%s
GROUP BY object_id
HAVING AVG(vote) > 0""" % connection.ops.quote_name(self.model._meta.db_table)
        if reversed:
            query += ' ORDER BY AVG(vote) ASC LIMIT %s'
        else:
            query += ' ORDER BY AVG(vote) DESC LIMIT %s'
        cursor = connection.cursor()
        cursor.execute(query, [ctype.id, limit])
        results = cursor.fetchall()

        # Use in_bulk() to avoid O(limit) db hits.
        objects = Model.objects.in_bulk([id for id, score in results])

        # Yield each object, score pair. Because of the lazy nature of generic
        # relations, missing objects are silently ignored.
        for id, score in results:
            if id in objects:
                yield objects[id], score

    def get_bottom(self, Model, limit=10):
        """
        Get the bottom (i.e. most negative) N scored objects for a given model.

        Yields (object, score) tuples.
        """
        return self.get_top(Model, limit, True)

    def get_for_user(self, obj, user):
        """
        Get the vote made on the given object by the given user, or
        ``None`` if no matching vote exists.
        """
        if not user.is_authenticated():
            return None
        ctype = ContentType.objects.get_for_model(obj)
        try:
            vote = self.get(content_type=ctype, object_id=obj.id, user=user)
        except Vote.DoesNotExist:
            vote = None
        return vote

    def get_for_user_in_bulk(self, objects, user):
        """
        Get a dictionary mapping object ids to votes made by the given
        user on the corresponding objects.
        """
        vote_dict = {}
        if len(objects) > 0:
            ctype = ContentType.objects.get_for_model(objects[0])
            votes = list(self.filter(content_type__pk=ctype.id,
                                     object_id__in=[obj.id for obj in objects],
                                     user__pk=user.id))
            vote_dict = dict([(vote.object_id, vote) for vote in votes])
        return vote_dict


class Vote(models.Model):
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')
    vote = models.SmallIntegerField(_(u'vote'), choices=get_vote_choices())

    objects = VoteManager()

    class Meta:
        verbose_name = _(u'vote')
        verbose_name_plural = _(u'votes')

    def __unicode__(self):
        return u'%s: %s on %s' % (self.user, self.vote, self.object)
