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

from merengue.collection.models import Collection
from merengue.collection.views import collection_view

BANNER_COLLECTION_SLUG = 'banners'


def banner_index(request, template_name='banner/banner_index.html'):
    banner_list = get_collection_banner()
    return collection_view(request, banner_list, template_name=template_name)


def get_banners(request=None, limit=None, filtering_section=None):
    collection = get_collection_banner()
    section = None
    if request and request.section:
        section = request.section
    return collection.get_items(section, filtering_section)[:limit]


def get_collection_banner():
    return Collection.objects.get(
        slug=BANNER_COLLECTION_SLUG)
