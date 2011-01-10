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

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

from cmsutils.adminfilters import QueryStringManager
from merengue.base.views import content_view, content_list
from merengue.collection.models import Collection
from plugins.news.models import NewsItem, NewsCategory


NEWS_COLLECTION_SLUG = 'news_collection'


def news_index(request, queryset=None, extra_context=None):
    (news_collection, created) = Collection.objects.get_or_create(slug=NEWS_COLLECTION_SLUG)
    if created:
        news_collection.name_es = 'Noticias'
        news_collection.name_en = 'News'
        news_collection.include_filters.create(filter_field='status',
                                               filter_operator='exact',
                                               filter_value='published')
        news_collection.content_types.add(ContentType.objects.get_for_model(NewsItem))
        news_collection.save()
    return content_view(request, news_collection, extra_context=extra_context)


def newsitem_view(request, newsitem_slug, extra_context=None):
    newsitem = get_object_or_404(NewsItem, slug=newsitem_slug)
    return content_view(request, newsitem, 'news/newsitem_view.html', extra_context=extra_context)


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


def get_news(request=None, limit=0, queryset=None):
    queryset = queryset or NewsItem.objects.published()
    news = queryset.order_by("-publish_date")
    qsm = QueryStringManager(request, page_var='page', ignore_params=('set_language', ))
    filters = qsm.get_filters()
    try:
        news = news.filter(**filters)
    except:
        pass
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
