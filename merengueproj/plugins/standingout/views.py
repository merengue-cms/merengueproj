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
from django.contrib.contenttypes.models import ContentType

from merengue.base.views import content_list

from cmsutils.adminfilters import QueryStringManager

from plugins.standingout.models import StandingOut


def standingout_list(request, filters=None, extra_context=None):
    filters = filters or {}
    filters_section = {}
    section = None
    standingouts = None
    standingouts_base = get_standingouts().filter(**filters)
    if extra_context and 'section' in extra_context:
        section = extra_context['section']
        filters_section['related_id'] = section.id
        filters_section['related_content_type'] = ContentType.objects.get_for_model(section)
        filters_section.update(filters)
        standingouts = standingouts_base.filter(**filters_section)
    if not standingouts:
        standingouts = standingouts_base.filter(related_content_type__isnull=True,
                                                        related_id__isnull=True)
    return content_list(request, standingouts,
                        template_name='standingout/standingout_list.html',
                        extra_context=extra_context)


def get_standingouts(request=None, limit=0):
    standingouts = StandingOut.objects.all()
    qsm = QueryStringManager(request, page_var='page', ignore_params=('set_language', ))
    filters = qsm.get_filters()
    standingouts = standingouts.filter(**filters)
    if limit:
        return standingouts[:limit]
    else:
        return standingouts
