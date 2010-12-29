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
from merengue.base.views import content_list

from cmsutils.adminfilters import QueryStringManager

from plugins.standingout.models import StandingOut


def standingout_list(request, filters=None):
    filters = {}
    standingouts = get_standingouts().filter(**filters)
    return content_list(request, standingouts,
                        template_name='standingout/standingout_list.html')


def get_standingouts(request=None, limit=0):
    standingouts = StandingOut.objects.all()
    qsm = QueryStringManager(request, page_var='page', ignore_params=('set_language', ))
    filters = qsm.get_filters()
    standingouts = standingouts.filter(**filters)
    if limit:
        return standingouts[:limit]
    else:
        return standingouts
