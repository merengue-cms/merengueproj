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

from django.contrib.auth.models import User
from django.db.models import Q


class UserLookup(object):

    def get_query(self, q, request):
        """ return a query set. you also have access to request.user if needed """
        return User.objects.filter(Q(username__istartswith=q) | Q(first_name__istartswith=q) | Q(last_name__istartswith=q))

    def format_item(self, user):
        """ simple display of an object when it is displayed in the list of selected objects """
        return unicode(user.get_full_name())

    def format_result(self, user):
        """ a more verbose display, used in the search results display.  may contain html and multi-lines """
        return u"%s %s (%s)" % (user.first_name, user.last_name, user.username)

    def get_objects(self, ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return User.objects.filter(pk__in=ids).order_by('first_name', 'last_name')
