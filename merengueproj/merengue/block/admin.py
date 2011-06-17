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

from django.contrib.admin.filterspecs import FilterSpec
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import RelatedModelAdmin, related_form_clean
from merengue.base.models import BaseContent
from merengue.block.models import RegisteredBlock
from merengue.block.filterspecs import ContentBlockFilterSpec
from merengue.block.forms import BaseContentRelatedBlockAddForm, BaseContentRelatedBlockChangeForm
from merengue.registry.admin import RegisteredItemAdmin


# Don't call register but insert it at the beginning of the registry
# otherwise, the AllFilterSpec will be taken first
FilterSpec.filter_specs.insert(0, (lambda f: f.name == 'content' and f.model == RegisteredBlock,
                               ContentBlockFilterSpec))


class RegisteredBlockAdmin(RegisteredItemAdmin):
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name', )
    list_display = RegisteredItemAdmin.list_display + ('name', 'placed_at', )
    list_filter = ('placed_at', 'content')
    search_fields = ('name', )
    ordering = ('order', )
    change_form_template = 'admin/block/change_form.html'

    fieldsets = (
        ('', {'fields': ('name', 'module', 'class_name', )}),
        (_('Status'),
            {'fields': ('placed_at', 'active', 'shown_in_urls', 'hidden_in_urls', 'order', 'config')}
        ),
        (_('Cache parameters'),
            {'fields': ('is_cached', 'cache_timeout', 'cache_only_anonymous', 'cache_vary_on_user', 'cache_vary_on_url', 'cache_vary_on_language', )}
        ))

    class Media:
        js = ('merengue/js/block/caching.js', )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(RegisteredBlockAdmin, self).get_readonly_fields(request, obj)
        if obj and obj.is_fixed:
            readonly_fields += ('placed_at', 'order', 'active')
        elif obj and obj.fixed_place:
            readonly_fields += ('placed_at', )

        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(RegisteredBlockAdmin, self).get_fieldsets(request, obj)
        if obj and not obj.get_registry_item().cache_allowed:
            fieldsets = fieldsets[0:2]  # remove the cache parameters
        return fieldsets

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        is_cacheable = obj and obj.get_registry_item().cache_allowed or False
        context.update({
            'is_cacheable': is_cacheable,
        })
        return super(RegisteredBlockAdmin, self).render_change_form(request, context, add, change, form_url, obj)

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

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            form = self.get_form(request, obj)
            fields = form.base_fields.keys()
            return [(None, {'fields': fields})]  # not included the readonly_fields
        else:
            return super(BaseContentRelatedBlockAdmin, self).get_fieldsets(request, obj)

    def add_view(self, request, form_url='', extra_context=None, parent_model_admin=None, parent_object=None):
        return super(BaseContentRelatedBlockAdmin, self).add_view(request, form_url, extra_context, parent_model_admin)

    def get_form(self, request, obj=None, **kwargs):
        if request.get_full_path().endswith('add/'):
            form = BaseContentRelatedBlockAddForm
            form.clean = related_form_clean(self.related_field, self.basecontent)
        else:
            form = super(BaseContentRelatedBlockAdmin, self).get_form(request, obj, **kwargs)
        return form


def register(site):
    site.register(RegisteredBlock, RegisteredBlockAdmin)
    site.register_related(RegisteredBlock, BaseContentRelatedBlockAdmin,
                          related_to=BaseContent)
