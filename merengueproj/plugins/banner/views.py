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

from cmsutils.adminfilters import QueryStringManager
from merengue.base.views import content_list
from plugins.banner.models import Banner


def banner_index(request, template_name='banner/banner_index.html'):
    banner_list = get_banners(request)
    return content_list(request, banner_list, template_name=template_name)


def get_banners(request=None, limit=0):
    banners = Banner.objects.published()
    qsm = QueryStringManager(request, page_var='page', ignore_params=('set_language', ))
    filters = qsm.get_filters()
    banners = banners.filter(**filters)
    if limit:
        return banners[:limit]
    else:
        return banners
