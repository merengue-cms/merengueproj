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

from merengue.viewlet.viewlets import Viewlet
from plugins.news.views import get_news


class LatestNewsViewlet(Viewlet):
    name = 'latestnews'
    help_text = _('Latest news')
    verbose_name = _('Latest news block')

    @classmethod
    def render(cls, request):
        news_list = get_news(request, 10)
        return cls.render_viewlet(request, template_name='news/viewlet_latest.html',
                                  context={'news_list': news_list})


class AllNewsViewlet(Viewlet):
    name = 'allnews'
    help_text = _('All news')
    verbose_name = _('All news block')

    @classmethod
    def render(cls, request):
        news_list = get_news(request)
        return cls.render_viewlet(request, template_name='news/viewlet_latest.html',
                                  context={'news_list': news_list,
                                           'is_paginated': True,
                                           'paginate_by': 10})
