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

from django.conf import settings


def section(request):
    # simplest context processor ever :-)
    enable_document_sections = getattr(settings, 'ENABLE_DOCUMENT_SECTIONS', True)
    section = getattr(request, 'section', None)
    if section and hasattr(section, 'get_real_instance'):
        section = section.get_real_instance()
    return {'section': section,
            'enable_document_sections': enable_document_sections}
