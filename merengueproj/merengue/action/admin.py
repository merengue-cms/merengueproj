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

from django.utils.translation import ugettext_lazy as _

from merengue.registry.admin import RegisteredItemAdmin
from merengue.action.models import RegisteredAction


class RegisteredActionAdmin(RegisteredItemAdmin):
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name', )
    list_display = ('class_name', 'module', 'active', )
    search_fields = ('name', )
    ordering = ('order', )

    fieldsets = (
        ('', {'fields': ('name', 'module', 'class_name', )}),
        (_('Status'),
            {'fields': ('active', 'order', 'config')}
        ))

    def has_add_permission(self, request):
        return False


def register(site):
    site.register(RegisteredAction, RegisteredActionAdmin)
