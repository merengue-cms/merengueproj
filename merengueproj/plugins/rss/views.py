# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.http import HttpResponse
from django.db.models import Q
from django.utils import feedgenerator
from django.template.loader import render_to_string
from merengue.base.models import BaseContent

from plugins.rss.config import PluginConfig


def rss_views(request):

    contenttypes = PluginConfig.get_config().get(
        'contenttypes', []).get_value()

    query = Q()
    if not contenttypes:
        results = BaseContent.objects.filter(
            status='published').order_by('modification_date')[::-1]
    else:
        classnames = [x for x in contenttypes]
        for classname in classnames:
            query = query | Q(class_name=classname)
            results = BaseContent.objects.filter(status='published').filter(
                query).order_by('modification_date')[::-1]

    f = feedgenerator.Rss201rev2Feed(
        title=render_to_string('rss/title.html'),
        link=render_to_string('rss/link.html'),
        description=render_to_string('rss/description.html'),
        language=render_to_string('rss/language.html'),
        author_name=render_to_string('rss/author_name.html'),
        feed_url=render_to_string('rss/feed_url.html'),
    )
    limit = PluginConfig.get_config().get('limit', None)
    results = results[:int(limit.get_value())]
    for item in results:
        if 'modification_date' in item.__dict__:
            item_date = item.modification_date
        else:
            item_date = datetime.now()
        f.add_item(
            title=render_to_string('rss/items/title.html',
                                   {'item': item}),
            link=render_to_string('rss/items/link.html',
                                  {'item': item}),
            pubdate=item_date,
            description=render_to_string('rss/items/description.html',
                                         {'item': item}),
        )

    return HttpResponse(f.writeString('UTF-8'),
                        mimetype="application/atom+xml")