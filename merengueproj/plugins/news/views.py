from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

from cmsutils.adminfilters import QueryStringManager
from merengue.base.views import content_view, content_list
from plugins.news.models import NewsItem, NewsCategory


def news_index(request):
    news_list = get_news(request)
    news_category_slug = request.GET.get('categories__slug', None)
    news_category = news_category_slug and get_object_or_404(NewsCategory, slug=news_category_slug)
    return content_list(request, news_list, template_name='news/news_index.html', extra_context={'news_category': news_category})


def newsitem_view(request, newsitem_slug):
    newsitem = get_object_or_404(NewsItem, slug=newsitem_slug)
    return content_view(request, newsitem, 'news/newsitem_view.html')


def newsitem_by_category_view(request, newscategory_slug):
    if request.is_ajax():
        newscategory = NewsCategory.objects.get(slug=newscategory_slug)
        news_string = render_to_string('news/newsitem_by_category.html',
                                       {'news_category_active': newscategory,
                                       },
                                       context_instance=RequestContext(request))
        return HttpResponse(news_string, mimetype='txt/html')
    return HttpResponseRedirect('/')


def news_by_date(request, year, month, day):
    news = get_news_by_date(request, year, month, day)
    return content_list(request, news, template_name='news/news_index.html')


def get_news(request=None, limit=0):
    news = NewsItem.objects.published().order_by("-publish_date")
    qsm = QueryStringManager(request, page_var='page', ignore_params=('set_language', ))
    filters = qsm.get_filters()
    news = news.filter(**filters)
    if limit:
        return news[:limit]
    else:
        return news


def get_news_by_date(request, year, month, day):
    news = get_news(request)
    news = news.filter(publish_date__year=year,
                       publish_date__month=month,
                       publish_date__day=day)
    return news
