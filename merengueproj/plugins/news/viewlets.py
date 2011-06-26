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

from merengue.viewlet.viewlets import Viewlet
from merengue.registry import params
from merengue.registry.items import ViewLetQuerySetItemProvider

from plugins.news.models import NewsItem


class LatestNewsViewlet(ViewLetQuerySetItemProvider, Viewlet):
    name = 'latestnews'
    help_text = _('Latest news')
    verbose_name = _('Latest news block')

    config_params = ViewLetQuerySetItemProvider.config_params + [
        params.PositiveInteger(name='limit', label=ugettext('limit for news viewlet'),
                      default=3),
    ]

    def queryset(self, request, context, section):
        limit = self.get_config().get('limit').get_value()
        return NewsItem.objects.published()[:limit]

    def render(self, request, context=None):
        if context is None:
            context = {}
        news_list = self.get_queryset(request, context)
        context.update({'news_list': news_list})
        return self.render_viewlet(request, template_name='news/viewlet_latest.html',
                                   context=context)


class AllNewsViewlet(ViewLetQuerySetItemProvider, Viewlet):
    name = 'allnews'
    help_text = _('All news')
    verbose_name = _('All news block')

    def queryset(self, request, context, section):
        return NewsItem.objects.published()

    def render(self, request, context=None):
        if context is None:
            context = {}
        news_list = self.get_queryset(request, context)
        context.update({
            'news_list': news_list,
            'is_paginated': True,
            'paginate_by': 10,
        })
        return self.render_viewlet(request, template_name='news/viewlet_latest.html',
                                   context=context)
