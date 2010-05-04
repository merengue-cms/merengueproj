from django.utils.translation import ugettext as _

from merengue.viewlet.viewlets import Viewlet
from plugins.news.models import NewsItem


class LatestNewsViewlet(Viewlet):
    name = 'latestnews'
    label = _('Latest news')

    @classmethod
    def render(cls, request):
        news_list = NewsItem.objects.published().order_by('-publish_date')[:5]
        return cls.render_viewlet(request, template_name='news/viewlet_latest.html',
                                  context={'news_list': news_list})


class AllNewsViewlet(Viewlet):
    name = 'allnews'
    label = _('All news')

    @classmethod
    def render(cls, request):
        news_list = NewsItem.objects.published().order_by('-publish_date')
        return cls.render_viewlet(request, template_name='news/viewlet_latest.html',
                                  context={'news_list': news_list})
