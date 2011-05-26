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

from merengue.base.lookups import ContentLookup
from merengue.base.models import BaseContent


class ContentLinkLookup(ContentLookup):

    def get_query(self, q, request):
        """ return a query set. you also have access to request.user if needed """
        section = request.GET.get('section', None)
        limit = request.GET.get('limit', 10)
        autocompleted = BaseContent.objects.filter(self._get_filters(q))
        if section:
            # we give priority to the contents inside section
            autocompleted = list(autocompleted.filter(sections=section)[:limit].visible_by_user(request.user)) + \
                list(autocompleted.exclude(sections=section)[:limit].visible_by_user(request.user))
        else:
            autocompleted = autocompleted[:limit]
        return autocompleted
