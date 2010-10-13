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

from django.shortcuts import get_object_or_404

from cmsutils.adminfilters import QueryStringManager
from merengue.base.views import content_view, content_list
from plugins.link.models import Link, LinkCategory


def link_index(request, template_name='link/link_index.html', queryset=None, extra_context=None):
    link_list = get_links(request, queryset=queryset)
    link_category_slug = request.GET.get('categories__slug', None)
    link_category = link_category_slug and get_object_or_404(LinkCategory, slug=link_category_slug)
    context = {'link_category': link_category}
    extra_context = extra_context or {}
    context.update(extra_context)
    return content_list(request, link_list, template_name=template_name, extra_context=context)


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
