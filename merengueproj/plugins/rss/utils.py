# Copyright (c) 2011 by Yaco Sistemas
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

from django.db.models import Q
from django.contrib.sites.models import Site
from django.utils import feedgenerator
from django.template.loader import render_to_string

from merengue.base.models import BaseContent
from merengue.registry.items import ALL_TYPES

from merengue.pluggable.utils import get_plugin


def generate_feed_from_queryset(queryset=None):
    plugin = get_plugin('rss')

    if not queryset:
        contenttypes = plugin.get_config().get(
            'contenttypes', []).get_value()
        query = Q()
        if not contenttypes or ALL_TYPES in contenttypes:
            queryset = BaseContent.objects.filter(
                status='published').order_by('modification_date')[::-1]
        else:
            classnames = [x for x in contenttypes]
            for classname in classnames:
                query = query | Q(class_name=classname.lower())
                queryset = BaseContent.objects.filter(
                    status='published').filter(
                    query).order_by('modification_date')[::-1]

    portal_title = plugin.get_config().get(
        'portal', '').get_value()
    f = feedgenerator.Rss201rev2Feed(
        title=portal_title,
        link=render_to_string('rss/link.html'),
        description=render_to_string('rss/description.html'),
        language=render_to_string('rss/language.html'),
        author_name=render_to_string('rss/author_name.html'),
        feed_url=render_to_string('rss/feed_url.html'),
    )
    limit = plugin.get_config().get('limit', None)
    queryset = queryset[:int(limit.get_value())]
    link_prefix = 'http://%s' % Site.objects.all()[0].domain
    for item in queryset:
        if hasattr(item, 'get_real_instance'):
            item = item.get_real_instance()
        if 'modification_date' in item.__dict__:
            item_date = item.modification_date
        else:
            item_date = datetime.now()
        templates = {'title': ['rss/%s/title.html' % item.class_name,
                               'rss/items/title.html'],
                     'description': ['rss/%s/description.html' % item.class_name,
                               'rss/items/description.html'],
                    }
        f.add_item(
            title=render_to_string(templates['title'], {'item': item}),
            link=u'%s%s' % (link_prefix, item.public_link()),
            pubdate=item_date,
            description=render_to_string(templates['description'],
                                         {'item': item}),
        )

    return f.writeString('UTF-8')
