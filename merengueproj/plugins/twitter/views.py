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
from django.shortcuts import render

from merengue.block.models import RegisteredBlock

from plugins.twitter.utils import twitter_api


def get_user_tweets(request, block_id):
    block = RegisteredBlock.objects.get(id=block_id)

    limit = block.get_config().get('limit', [])
    user = block.get_config().get('user', [])

    api = twitter_api(limit, user)
    (user_tweets, error) = api.get_user_tweets()

    tweets = {'error': error, 'list': api.render_tweets(user_tweets, False)}

    return HttpResponse(render(request=request,
                               template_name='twitter/list_tweets.html',
                               dictionary={'tweets': tweets}), 'text/html')


def get_hashtag_tweets(request, block_id):
    block = RegisteredBlock.objects.get(id=block_id)

    limit = block.get_config().get('limit', [])
    hashtag = block.get_config().get('hashtag', [])

    api = twitter_api(limit, hashtag)
    (hashtag_tweets, error) = api.get_hashtags_tweets()

    tweets = {'error': error, 'list': api.render_tweets(hashtag_tweets)}

    return HttpResponse(render(request=request,
                            template_name='twitter/list_tweets.html',
                            dictionary={'tweets': tweets}), 'text/html')
