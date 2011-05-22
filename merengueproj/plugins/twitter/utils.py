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

import re
import twitter


class twitter_api():
    def __init__(self, limit, value):
        self.api = twitter.Api()
        self.limit = limit
        self.value = value

    def get_user_tweets(self):
        try:
            if self.api.GetUser(self.value).protected:
                return ([], u'This user has protected his tweets')
            else:
                tweets = self.api.GetUserTimeline(screen_name=self.value,
                                                  count=self.limit,
                                                  include_rts=True)
                if not tweets:
                    return ([], u"This user hasn't tweets yet")

                else:
                    return (tweets, u'Ok')

        except twitter.TwitterError:
            return ([], u"This user doesn't exists")

    def get_hashtags_tweets(self):
        tweets = self.api.GetSearch(term=self.value,
                                    lang='all',
                                    per_page=self.limit,
                                    show_user=True)

        return (tweets, u"There aren't results for the hashtag defined")

    def convert_tweet_html(self, tweet):
        # check if exists a link on tweet
        if 'http' in tweet:
            pattern_url = re.compile("https?://[a-zA-Z0-9./-_]+")
            url = pattern_url.search(tweet)
            while url is not None:
                rpl = "<a href='" + url.group() + "'>" + url.group() + "</a>"
                pos = int(url.end()) + len(rpl) - len(url.group())

                tweet = tweet.replace(url.group(), rpl)
                url = pattern_url.search(tweet, pos)

        # check if exists '#' on tweet
        if '#' in tweet:
            pattern_tag = re.compile("#[a-zA-Z0-9]+")
            tag = pattern_tag.search(tweet)
            while tag is not None:
                rpl = "<a href='http://twitter.com/#!/search/" + tag.group()[1:] + \
                    "'>" + tag.group() + "</a>"
                pos = int(tag.end()) + len(rpl) - len(tag.group())

                tweet = tweet.replace(tag.group(), rpl)
                tag = pattern_tag.search(tweet, pos)

        # check if exists '@' on tweet
        if '@' in tweet:
            pattern_user = re.compile("@[a-zA-Z0-9_]+")
            user = pattern_user.search(tweet)
            while user is not None:
                rpl = "<a href='http://twitter.com/#!/" + user.group()[1:] + \
                    "'>" + user.group() + "</a>"
                pos = int(user.end()) + len(rpl) - len(user.group())

                tweet = tweet.replace(user.group(), rpl)
                user = pattern_user.search(tweet, pos)

        return tweet

    def render_tweets(self, tweets, with_name=True):
        tweets_dict = []

        for tweet in tweets:
            # Get user image (check if a retweet, and get the image for the real user)
            if tweet.retweeted_status:
                img = tweet.retweeted_status.user.profile_image_url
            else:
                img = tweet.user.profile_image_url
            if with_name:
                text = '@' + tweet.user.screen_name + ': ' + tweet.text
            else:
                text = tweet.text

            tweets_dict.append({'img': img,
                                'text': self.convert_tweet_html(text),
                                'time': tweet.relative_created_at})

        return tweets_dict
