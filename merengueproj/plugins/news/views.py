from django.shortcuts import render_to_response
from django.template import RequestContext

from plugins.news.models import NewsItem


def news_index(request):
    news_list = NewsItem.objects.published()
    return render_to_response('news/news_index.html',
                              {'news_list': news_list},
                              context_instance=RequestContext(request))
