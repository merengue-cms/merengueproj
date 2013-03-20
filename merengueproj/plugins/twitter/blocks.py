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

from django.utils.translation import ugettext_lazy as _, ugettext

from merengue.block.blocks import Block, BaseBlock
from merengue.registry import params


class TimelineProvider:
    template_name = ''
    block_title = ''

    def render(self, request, place, context, *args, **kwargs):
        return self.render_block(request, template_name=self.template_name,
                                 block_title=self.get_block_title(),
                                 context={})


class UserTimelineBlock(TimelineProvider, Block):
    name = 'usertimeline'
    default_place = 'rightsidebar'
    verbose_name = _('Timeline of Twitter User')
    help_text = _('Block to show a timeline of Twitter for an user.')
    template_name = 'twitter/timeline_block.html'

    config_params = BaseBlock.config_params + [params.PositiveInteger(name='limit',
                                            label=ugettext('Limit for twitter block'),
                                            default=3),
                     params.Single(name='user',
                                   label=ugettext('Tweets of this user'),
                                   default='merengueproject'),
                     ]

    def get_block_title(self):

        user = self.get_config().get('user', []).get_value()
        return "@%s" % user

    def get_link(self):
        error = self.get_tweets()
        if "doesn't exists" in error[1]:
            return ('Twitter Mainpage', 'http://www.twitter.com/')
        else:
            user = self.get_config().get('user', []).get_value()
            return ('Follow ' + user + ' on Twitter!', 'http://www.twitter.com/#!/' + user + '/')


class HashtagTimelineBlock(TimelineProvider, Block):
    name = 'hashtagtimeline'
    default_place = 'rightsidebar'
    verbose_name = _('Timeline of Tag in Twitter ')
    help_text = _('Block to show a timeline of Twitter for a hashtag.')
    template_name = 'twitter/hashtag_timeline_block.html'

    config_params = BaseBlock.config_params + [params.PositiveInteger(name='limit',
                                            label=ugettext('Limit for twitter block'),
                                            default=3),
                     params.Single(name='hashtag',
                                   label=ugettext('Tweets of a hashtag'),
                                   default='#merengueproject'),
                     ]

    def get_block_title(self):
        hashtag = self.get_config().get('hashtag', []).get_value()
        return hashtag

    def get_link(self):
        hashtag = self.get_config().get('hashtag', []).get_value()
        if hashtag.startswith('#'):
            return ('Search ' + hashtag + ' on Twitter!', 'http://www.twitter.com/#!/search/%23' + hashtag[1:] + '/')
        else:
            return ('Search ' + hashtag + ' on Twitter!', 'http://www.twitter.com/#!/search/' + hashtag + '/')
