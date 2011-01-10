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
from plugins.voting.models import Vote


def get_content_with_votes(request=None, limit=0, order_by='id'):
    votes = Vote.objects.all()
    contents = BaseContent.objects.published().filter(vote__in=votes)
    from copy import copy
    request_copy = copy_request(request, ['set_language'], copy)
    qsm = QueryStringManager(request, page_var='page')
    filters = qsm.get_filters()
    contents = contents.filter(**filters).distinct().select_related('votes').order_by(order_by)
    if limit:
        return contents[:limit]
    return contents


class BaseContentTopRated(Viewlet):
    name = 'basecontenttoprated'
    help_text = _('Content top rated')
    verbose_name = _('Top rated content')

    @classmethod
    def render(cls, request):
        votes_list = get_content_with_votes(request, limit=None, order_by='-vote__vote')
        return cls.render_viewlet(request, template_name='voting/viewlet_voting_basecontent.html',
                                  context={'votes_list': votes_list})


class BaseContentWithMoreVotes(Viewlet):
    name = 'basecontentwithmorevotes'
    help_text = _('Content that contains more votes')
    verbose_name = _('More votes content')

    @classmethod
    def render(cls, request):
        votes_list = get_content_with_votes(request, limit=None, order_by='-vote__num_votes')
        return cls.render_viewlet(request, template_name='voting/viewlet_voting_basecontent.html',
                                  context={'votes_list': votes_list})
