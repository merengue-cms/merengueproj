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

from django.utils.translation import ugettext_lazy as _

from cmsutils.adminfilters import QueryStringManager

from merengue.base.models import BaseContent
from merengue.utils import copy_request
from merengue.viewlet.viewlets import Viewlet
from merengue.registry.items import ViewLetQuerySetItemProvider

from plugins.voting.models import Vote


class BaseVotinViewlet(ViewLetQuerySetItemProvider, Viewlet):

    def get_contents(self, request=None, context=None, section=None):
        votes = Vote.objects.all()
        contents = BaseContent.objects.published().filter(vote__in=votes)
        return contents

    def get_content_with_votes(self, request=None, context=None, limit=0, order_by='id'):
        contents = self.get_queryset(request, context)
        from copy import copy
        request_copy = copy_request(request, ['set_language'], copy)
        qsm = QueryStringManager(request, page_var='page')
        filters = qsm.get_filters()
        contents = contents.filter(**filters).distinct().select_related('votes').order_by(order_by)
        if limit:
            return contents[:limit]
        return contents


class BaseContentTopRated(BaseVotinViewlet):
    name = 'basecontenttoprated'
    help_text = _('Content top rated')
    verbose_name = _('Top rated content')

    def render(self, request, context):
        votes_list = self.get_content_with_votes(request, context, limit=None, order_by='-vote__vote')
        return self.render_viewlet(request, template_name='voting/viewlet_voting_basecontent.html',
                                  context={'votes_list': votes_list})


class BaseContentWithMoreVotes(BaseVotinViewlet):
    name = 'basecontentwithmorevotes'
    help_text = _('Content that contains more votes')
    verbose_name = _('More votes content')

    def render(self, request, context):
        votes_list = self.get_content_with_votes(request, context, limit=None, order_by='-vote__num_votes')
        return self.render_viewlet(request, template_name='voting/viewlet_voting_basecontent.html',
                                  context={'votes_list': votes_list})
