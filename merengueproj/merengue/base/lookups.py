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

from django.db.models import Q
from django.contrib.auth.models import User

from transmeta import get_real_fieldname_in_each_language
from merengue.base.models import BaseContent


class ContentLookup(object):

    def _get_filters(self, q):
        name_fields = get_real_fieldname_in_each_language('name')
        filters = Q()  # query without filters
        for field_name in name_fields:
            filters |= Q(**{'%s__icontains' % field_name: q})
        return filters

    def get_query(self, q, request):
        """ return a query set. you also have access to request.user if needed """
        limit = request.GET.get('limit', 10)
        autocompleted = BaseContent.objects.filter(self._get_filters(q))[:limit].visible_by_user(request.user)
        return autocompleted

    def format_item(self, content):
        """ simple display of an object when it is displayed in the list of selected objects """
        content = content.get_real_instance()
        return u'%s (%s)' % (content, content._meta.verbose_name)

    def format_result(self, content):
        """ a more verbose display, used in the search results display.  may contain html and multi-lines """
        return self.format_item(content)

    def get_objects(self, ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return BaseContent.objects.filter(pk__in=ids)


class UserLookup(object):

    def get_query(self, q, request):
        """ return a query set. you also have access to request.user if needed """
        return User.objects.filter(Q(username__istartswith=q) | Q(first_name__istartswith=q) | Q(last_name__istartswith=q))

    def format_item(self, user):
        """ simple display of an object when it is displayed in the list of selected objects """
        full_name = user.get_full_name()
        if full_name:
            return u"%s (%s)" % (full_name, user.username)
        return user.username

    def format_result(self, user):
        """ a more verbose display, used in the search results display.  may contain html and multi-lines """
        return self.format_item(user)

    def get_objects(self, ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return User.objects.filter(pk__in=ids).order_by('first_name', 'last_name')
