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


from django.db.models import Q


def get_filter_ct(obj, field='related'):
    ctypes = [(c._meta.app_label, c._meta.module_name)for c in obj.__class__.mro() if getattr(c, '_meta', None)]
    filter_ctypes = Q()
    for app_label, module_name in ctypes:
        filter_ctypes = filter_ctypes | Q(**{'%s_content_type__app_label' % field: app_label,
                                             '%s_content_type__model' % field: module_name})
    return filter_ctypes


def get_section_standingouts(standingouts_base, section):
    standingouts = standingouts_base.filter(related_id=section.id).filter(get_filter_ct(section))
    standingouts = standingouts | standingouts_base.filter(belongs_to_section=section)
    return standingouts
