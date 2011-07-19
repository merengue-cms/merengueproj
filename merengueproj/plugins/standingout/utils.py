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


def get_filter_ct(obj):
    ctypes = [(c._meta.app_label, c._meta.module_name)for c in obj.__class__.mro() if getattr(c, '_meta', None)]
    filter_ctypes = Q()
    for app_label, module_name in ctypes:
        filter_ctypes = filter_ctypes | Q(related_content_type__app_label=app_label,
                                          related_content_type__model=module_name)
    return filter_ctypes
