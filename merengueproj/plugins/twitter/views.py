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


from django.http import HttpResponse
from django.utils.simplejson import dumps

from merengue.block.models import RegisteredBlock

from plugins.twitter.utils import twitter_api


def get_user_tweets(request, block_id):

    block = RegisteredBlock.objects.get(id=block_id)

    limit = block.get_config().get('limit', [])
    user = block.get_config().get('user', [])

    api = twitter_api(limit, user)
    (user_tweets, error) = api.get_user_tweets()

    render_tweets = []
    for tweet in user_tweets:
        render_tweets.append(api.convert_tweet_html(tweet))

    tweets = {'error': error, 'list': render_tweets}

    return HttpResponse(dumps(tweets), mimetype='text/json')


def get_hashtag_tweets(request, block_id):
    block = RegisteredBlock.objects.get(id=block_id)

    limit = block.get_config().get('limit', [])
    hashtag = block.get_config().get('hashtag', [])

    api = twitter_api(limit, hashtag)
    (hashtag_tweets, error) = api.get_hashtags_tweets()

    render_tweets = []
    for tweet in hashtag_tweets:
        render_tweets.append(api.convert_tweet_html(tweet))

    tweets = {'error': error, 'list': render_tweets}

    return HttpResponse(dumps(tweets), mimetype='text/json')
