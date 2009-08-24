from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from base.views import content_view
from plugins.news.models import NewsItem


def news_index(request):
    news_list = NewsItem.objects.published()
    return render_to_response('news/news_index.html',
                              {'news_list': news_list},
                              context_instance=RequestContext(request))


def newsitem_view(request, newsitem_slug):
    newsitem = get_object_or_404(NewsItem, slug=newsitem_slug)
    return content_view(request, newsitem, 'news/newsitem_view.html')
