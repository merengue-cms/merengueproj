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

from merengue.base.admin import RelatedModelAdmin, set_field_read_only
from merengue.base.models import BaseContent
from merengue.block.models import RegisteredBlock
from merengue.block.forms import BaseContentRelatedBlockAddForm, BaseContentRelatedBlockChangeForm
from merengue.perms import utils as perms_api
from merengue.registry.admin import RegisteredItemAdmin


class RegisteredBlockAdmin(RegisteredItemAdmin):
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name', )
    list_display = RegisteredItemAdmin.list_display + ('placed_at', )
    list_filter = ('placed_at', )
    ordering = ('order', )

    fieldsets = (
        ('', {'fields': ('name', 'module', 'class_name', )}),
        (_('Status'),
            {'fields': ('placed_at', 'active', 'shown_in_urls', 'hidden_in_urls', 'order', 'config')}
        ))

    def get_form(self, request, obj=None, **kwargs):
        form = super(RegisteredBlockAdmin, self).get_form(request, obj, **kwargs)
        if obj.is_fixed:
            for field_name in ('placed_at', 'order', 'active'):
                if field_name in form.base_fields:
                    set_field_read_only(form.base_fields[field_name], field_name, obj)
        return form

    def has_add_permission(self, request):
        return False


class BaseContentRelatedBlockAdmin(RelatedModelAdmin, RegisteredBlockAdmin):
    tool_name = 'block_content_related'
    tool_label = _('block content related')
    related_field = 'content'
    change_form_template = 'admin/block/related_block_admin.html'
    form = BaseContentRelatedBlockChangeForm
    fieldsets = RegisteredBlockAdmin.fieldsets + (
       (_('Visibility when duplicated blocks'),
            {'fields': ('overwrite_if_place', 'overwrite_always', )}),
    )

    def has_add_permission(self, request):
        return perms_api.can_manage_site(request.user)

    def add_view(self, request, form_url='', extra_context=None, parent_model_admin=None, parent_object=None):
        self.fieldsets = None  # fieldsets was cleared in add view
        return super(BaseContentRelatedBlockAdmin, self).add_view(request, form_url, extra_context, parent_model_admin)

    def get_form(self, request, obj=None, **kwargs):
        if request.get_full_path().endswith('add/'):
            return BaseContentRelatedBlockAddForm
        else:
            return super(BaseContentRelatedBlockAdmin, self).get_form(request, obj, **kwargs)


def register(site):
    site.register(RegisteredBlock, RegisteredBlockAdmin)
    site.register_related(RegisteredBlock, BaseContentRelatedBlockAdmin,
                          related_to=BaseContent)
