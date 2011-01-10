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

from django.shortcuts import get_object_or_404

from cmsutils.adminfilters import QueryStringManager
from merengue.base.views import content_view
from merengue.collection.models import Collection
from plugins.link.models import Link


LINK_COLLECTION_SLUG = 'links'


def link_index(request, extra_context=None):
    link_collection= Collection.objects.get(slug=LINK_COLLECTION_SLUG)
    extra_context = extra_context or {}
    return content_view(request, link_collection, extra_context=extra_context)


def link_view(request, link_slug, template_name='link/link_view.html', extra_context=None):
    link = get_object_or_404(Link, slug=link_slug)
    return content_view(request, link, template_name, extra_context=None)


def get_links(request=None, limit=0, queryset=None):
    queryset = queryset or Link.objects.published()
    links = queryset
    qsm = QueryStringManager(request, page_var='page', ignore_params=('set_language', ))
    filters = qsm.get_filters()
    links = links.filter(**filters)
    if limit:
        return links[:limit]
    else:
        return links
