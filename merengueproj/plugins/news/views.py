from django.shortcuts import get_object_or_404

from merengue.base.views import content_view, content_list
from plugins.news.models import NewsItem


def news_index(request):
    news_list = NewsItem.objects.published()
    return content_list(request, news_list, template_name='news/news_index.html')


def newsitem_view(request, newsitem_slug):
    newsitem = get_object_or_404(NewsItem, slug=newsitem_slug)
    return content_view(request, newsitem, 'news/newsitem_view.html')
