from django.utils.translation import ugettext as _

from merengue.viewlet.viewlets import Viewlet
from plugins.news.views import get_news


class LatestNewsViewlet(Viewlet):
    name = 'latestnews'
    label = _('Latest news')

    @classmethod
    def render(cls, request):
        news_list = get_news(request, 10)
        return cls.render_viewlet(request, template_name='news/viewlet_latest.html',
                                  context={'news_list': news_list})


class AllNewsViewlet(Viewlet):
    name = 'allnews'
    label = _('All news')

    @classmethod
    def render(cls, request):
        news_list = get_news(request)
        return cls.render_viewlet(request, template_name='news/viewlet_latest.html',
                                  context={'news_list': news_list,
                                           'is_paginated': True,
                                           'paginate_by': 10})
