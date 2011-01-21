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


def get_section(request=None, context=None):
    section = (request and getattr(request, 'section', None)) or (context and context.get('section', None))
    return section and section.real_instance


def filtering_in_section(queryset, section=None):
    if not section:
        return queryset
    if not queryset.query.can_filter():
        queryset = queryset.model.objects.filter(id__in=queryset.values('id').query)
    queryset = queryset.filter(basesection=section)
    return queryset
