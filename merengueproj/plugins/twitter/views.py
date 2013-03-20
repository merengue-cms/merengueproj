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
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page

from merengue.block.models import RegisteredBlock

from plugins.twitter.utils import twitter_api


@cache_page(60 * 5)
def get_user_tweets(request, block_id):
    block = RegisteredBlock.objects.get(id=block_id)

    limit = block.get_config().get('limit', [])
    user = block.get_config().get('user', [])

    (user_tweets, error) = twitter_api.get_user_tweets(user, limit)

    tweets = {'error': error, 'list': twitter_api.render_tweets(user_tweets, True)}

    if "doesn't exists" in error:
        link = (_('Twitter Mainpage'), 'http://www.twitter.com/')
    else:
        link = (_('Follow %(username)s on Twitter!') % {'username': user}, 'http://www.twitter.com/#!/' + user + '/')

    return HttpResponse(render(request=request,
                               template_name='twitter/list_tweets.html',
                               dictionary={'tweets': tweets, 'link': link}), 'text/html')


@cache_page(90)
def get_hashtag_tweets(request, block_id):
    block = RegisteredBlock.objects.get(id=block_id)

    limit = block.get_config().get('limit', [])
    hashtag = block.get_config().get('hashtag', [])

    (hashtag_tweets, error) = twitter_api.get_hashtags_tweets(hashtag, limit)

    tweets = {'error': error, 'list': twitter_api.render_tweets(hashtag_tweets)}

    if hashtag.startswith('#'):
        link = (_('Search %(hashtag)s on Twitter!') % {'hashtag': hashtag}, 'http://www.twitter.com/#!/search/%23' + hashtag[1:] + '/')
    else:
        link = (_('Search %(hashtag)s on Twitter!') % {'hashtag': hashtag}, 'http://www.twitter.com/#!/search/' + hashtag + '/')

    return HttpResponse(render(request=request,
                            template_name='twitter/list_tweets.html',
                            dictionary={'tweets': tweets, 'link': link}), 'text/html')
