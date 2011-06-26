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

from merengue.base.admin import BaseOrderableAdmin, set_field_read_only
from merengue.perms import utils as perms_api
from merengue.registry import is_broken
from merengue.registry.models import RegisteredItem


class RegisteredItemAdmin(BaseOrderableAdmin):
    readonly_fields = ('class_name', 'module', 'category', )
    list_display = ('class_name', 'module', 'category', 'active', )
    list_filter = ('category', )
    change_form_template = 'admin/registry/change_form.html'
    sortablefield = 'order'

    fieldsets = (
        ('', {'fields': ('module', 'class_name', )}),
        (_('Status'),
            {'fields': ('active', 'order', 'config', )}
        ),
    )

    def has_change_permission(self, request, obj=None):
        return perms_api.can_manage_site(request.user)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if obj:
            return obj.can_delete(request.user)
        return True

    def get_form(self, request, obj=None, **kwargs):
        form = super(RegisteredItemAdmin, self).get_form(request, obj,
                                                         **kwargs)
        broken_item = is_broken(obj)

        if broken_item:
            # a broken registered item will be not editable by anybody
            for field_name, field in form.base_fields.items():
                set_field_read_only(field, field_name, obj)

        if not broken_item and 'config' in form.base_fields.keys():
            config = obj.get_registry_item().get_config()
            config_field = form.base_fields['config']
            config_field.set_config(config)

        return form

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        broken_item = obj and is_broken(obj) or False
        context.update({
            'is_broken': broken_item,
        })
        return super(RegisteredItemAdmin, self).render_change_form(request, context, add, change, form_url, obj)


def register(site):
    site.register(RegisteredItem, RegisteredItemAdmin)
