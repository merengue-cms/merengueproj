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

from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

from merengue.base.views import content_view
from merengue.collection.models import Collection
from merengue.collection.views import collection_view
from plugins.news.models import NewsItem, NewsCategory


NEWS_COLLECTION_SLUG = 'news'


def news_index(request, extra_context=None, template_name='news/news_index.html'):
    news_collection = get_collection_news()
    return collection_view(request, news_collection, extra_context=extra_context, template_name=template_name)


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
    news_collection = get_collection_news()
    try:
        date = datetime(int(year), int(month), int(day))
    except ValueError:
        raise Http404()
    extra_context = {'_filters_collection': dict(publish_date__year=year,
                                             publish_date__month=month,
                                             publish_date__day=day),
                     'date': date}
    return collection_view(request, news_collection, extra_context=extra_context,
                           template_name='news/news_index.html')


def get_news(request=None, limit=None, filtering_section=None):
    collection = get_collection_news()
    section = None
    if request and request.section:
        section = request.section
    return collection.get_items(section, filtering_section)[:limit]


def get_collection_news():
    return get_object_or_404(Collection, slug=NEWS_COLLECTION_SLUG)
