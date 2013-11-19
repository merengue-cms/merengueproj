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
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import translation
from django.utils.translation import trans_null, trans_real

from rating.models import Vote
from rating.templatetags.rating_tags import get_score_info


class Item(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class VoteManagerTests(TestCase):

    def test_get_top(self):
        user = User.objects.create_user(username='tester1',
                                        email='tester1@testland.com',
                                        password='secret')
        items = []
        votes = [2, 3, 1, 4, 1, 5]
        for i, vote in enumerate(votes):
            item = Item.objects.create(name=str(i))
            Vote.objects.record_vote(item, user, vote)
            items.append(item)

        top = list(Vote.objects.get_top(Item, limit=3))
        self.assertEquals(top[0][0].name, '5')
        self.assertEquals(top[0][1], 5)
        self.assertEquals(top[1][0].name, '3')
        self.assertEquals(top[1][1], 4)
        self.assertEquals(top[2][0].name, '1')
        self.assertEquals(top[2][1], 3)


class NoI18nTestCase(TestCase):

    def setUp(self):
        # There are two ways of deactivating translation:
        #  1. Using a custom test_runner that set settings.USE_I18N to False
        #  2. Monkey patching the following function
        translation.real_activate = trans_null.activate
        translation.real_ugettext = trans_null.ugettext
        translation.deactivate()

    def tearDown(self):
        if settings.USE_I18N:
            translation.real_activate = trans_real.activate
            translation.real_ugettext = trans_real.ugettext


class ViewsTests(NoI18nTestCase):
    urls = 'rating.urls'

    def setUp(self):
        super(ViewsTests, self).setUp()

        self.item = Item.objects.create(name='foo')
        self.content_type = ContentType.objects.get_for_model(Item)

    def test_anonymous_can_not_rate(self):
        response = self.client.post('/rate/%d/%d/' % (self.content_type.id,
                                                      self.item.id))
        self.assertContains(response, 'Permission denied', status_code=403)

    def test_regular_vote(self):
        score = Vote.objects.get_score(self.item)
        self.assertEquals(score['score'], 0)
        self.assertEquals(score['num_votes'], 0)

        user1 = User.objects.create_user(username='tester1',
                                         email='tester1@testland.com',
                                         password='secret')
        self.assert_(self.client.login(username='tester1', password='secret'))

        url = '/rate/%d/%d/' % (self.content_type.id, self.item.id)
        response = self.client.post(url, {'vote': 3})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], 'http://testserver/')

        score = Vote.objects.get_score(self.item)
        self.assertEquals(score['score'], 3)
        self.assertEquals(score['num_votes'], 1)

        # vote again with the same user
        response = self.client.post(url, {'vote': 2})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], 'http://testserver/')

        score = Vote.objects.get_score(self.item)
        self.assertEquals(score['score'], 2)
        self.assertEquals(score['num_votes'], 1)

        # vote with a different user
        self.client.logout()
        user2 = User.objects.create_user(username='tester2',
                                         email='tester2@testland.com',

                                         password='secret')

        self.assert_(self.client.login(username='tester2', password='secret'))
        response = self.client.post(url, {'vote': 4})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], 'http://testserver/')

        score = Vote.objects.get_score(self.item)
        self.assertEquals(score['score'], 3) # average of votes
        self.assertEquals(score['num_votes'], 2)

    def test_vote_ranges(self):
        user1 = User.objects.create_user(username='tester1',
                                         email='tester1@testland.com',
                                         password='secret')
        self.assert_(self.client.login(username='tester1', password='secret'))
        # vote the maximum allowed
        url = '/rate/%d/%d/' % (self.content_type.id, self.item.id)
        response = self.client.post(url, {'vote': 5})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], 'http://testserver/')

        score = Vote.objects.get_score(self.item)
        self.assertEquals(score['score'], 5)
        self.assertEquals(score['num_votes'], 1)

        response = self.client.post(url, {'vote': 1})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], 'http://testserver/')

        score = Vote.objects.get_score(self.item)
        self.assertEquals(score['score'], 1)
        self.assertEquals(score['num_votes'], 1)

    def test_ajax_rating(self):
        score = Vote.objects.get_score(self.item)
        self.assertEquals(score['score'], 0)
        self.assertEquals(score['num_votes'], 0)

        user1 = User.objects.create_user(username='tester1',
                                         email='tester1@testland.com',
                                         password='secret')
        self.assert_(self.client.login(username='tester1', password='secret'))

        url = '/rate/%d/%d/' % (self.content_type.id, self.item.id)
        response = self.client.post(url, {'vote': 3, 'is_ajax': True})
        self.assertContains(response, '1 vote', status_code=200)
        self.assertContains(response, '3</span>/5 stars', status_code=200)

        score = Vote.objects.get_score(self.item)
        self.assertEquals(score['score'], 3)
        self.assertEquals(score['num_votes'], 1)


class FakeRequest(dict):
    session = {}


class TemplateTagsTests(NoI18nTestCase):
    urls = 'rating.urls'

    def setUp(self):
        super(TemplateTagsTests, self).setUp()
        # change the template loaders so we don't depend on the project
        self.old_template_loaders = settings.TEMPLATE_LOADERS
        app_template_loader = 'django.template.loaders.app_directories.load_template_source'
        settings.TEMPLATE_LOADERS = [app_template_loader]

        self.item = Item.objects.create(name='foo')

    def tearDown(self):
        settings.TEMPLATE_LOADERS = self.old_template_loaders

    def test_get_score_info(self):
        vote = {'score': 4, 'num_votes': 3}
        score_info = get_score_info(vote)

        self.assertEqual(score_info['num_votes'], 3)
        self.assertEqual(score_info['current_score'], 4)
        self.assertEqual(score_info['current_rating_width'], 68)
        self.assertEqual(score_info['num_stars'], 5)
        self.assertEqual(score_info['stars'],
                         [u'Very bad', u'Bad', u'OK', u'Good', u'Very good'])

    def test_ratingform_tag(self):
        context = template.Context({'obj': self.item, 'user': AnonymousUser(),
                                    'request': FakeRequest()})
        t = template.Template('{% load rating_tags %}{% ratingform obj %}')
        result = t.render(context)
        self.assert_('Sign in to rate' in result)
        self.assert_('0</span>/5' in result)

        user = User.objects.create_user(username='tester1',
                                        email='tester1@testland.com',
                                        password='secret')
        context = template.Context({'obj': self.item, 'user': user,
                                    'request': FakeRequest()})
        result = t.render(context)
        self.assert_('<input' in result)
        for rate in (u'Very bad', u'Bad', u'OK', u'Good',
                     u'Very good'):
            self.assert_(rate in result)

        t = template.Template('{% load rating_tags %}'
                              '{% ratingform obj readonly %}')
        result = t.render(context)
        self.assert_('<input' not in result)
