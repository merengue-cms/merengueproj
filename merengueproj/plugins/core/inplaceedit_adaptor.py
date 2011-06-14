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


from merengue.perms.utils import has_global_permission

# Edit your settings.py to override the default permissions of inplaceeditform:
#
# ADAPTOR_INPLACEEDIT_EDIT = 'plugins.core.inplaceedit_adaptor.MerengueEditAdaptor'


class MerengueEditAdaptor(object):

    @classmethod
    def can_edit(cls, adaptor):
        if hasattr(adaptor, 'request') and hasattr(adaptor.request, 'user') and\
            has_global_permission(adaptor.request.user, 'manage_site'):
            return True
        return False
