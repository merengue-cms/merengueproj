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
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from merengue.base.admin import set_field_read_only
from merengue.pluggable.checker import check_plugins
from merengue.pluggable.models import RegisteredPlugin
from merengue.pluggable.utils import has_required_dependencies
from merengue.registry.admin import RegisteredItemAdmin


class RegisteredPluginAdmin(RegisteredItemAdmin):
    change_form_template = 'admin/plugin/plugin_change_form.html'
    change_list_template = 'admin/plugin/plugin_change_list.html'
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name',
        'description', 'version', 'timestamp', 'directory_name', )
    list_display = ('name', 'directory_name', 'installed', 'active', 'screenshot_link', )

    fieldsets = (
        ('',
            {'fields': ('name', 'description', 'version', 'directory_name',
                        'module', 'class_name', 'required_apps',
                        'required_plugins', ), }
        ),
        (_('Status'),
            {'fields': ('installed', 'active', 'order', 'config'), },
        )
    )

    def get_form(self, request, obj=None):
        form = super(RegisteredPluginAdmin, self).get_form(request, obj)
        if not obj.installed:
            set_field_read_only(form.base_fields['active'], 'active', obj)
        if obj.directory_name in settings.REQUIRED_PLUGINS:
            # required plugins cannot being deactivated or uninstalled
            set_field_read_only(form.base_fields['active'], 'active', obj)
            set_field_read_only(form.base_fields['installed'], 'installed', obj)
        if not has_required_dependencies(obj):
            installed_field = form.base_fields['installed']
            help_text = installed_field.help_text
            installed_field.help_text = "%s %s" \
                                        % (help_text,
                                          _('Not all dependencies are met'))
            set_field_read_only(installed_field, 'installed', obj)
        # checking if plugin is broken
        if obj.broken:
            # a broken registered item will be not editable by anybody
            for field_name, field in form.base_fields.items():
                set_field_read_only(field, field_name, obj)

        return form

    def save_form(self, request, form, change):
        if 'installed' in form.changed_data:
            if form.cleaned_data['installed'] == True:
                # it has no sense install a plugin without activate
                form.cleaned_data['active'] = True
            else:
                form.cleaned_data['active'] = False
        return form.save(commit=False)

    def has_add_permission(self, request):
        return False

    def screenshot_link(self, obj):
        if not obj.screenshot:
            return ugettext('None')
        return mark_safe(u'<a href="%s" target="_blank">%s</a>' % (obj.screenshot, ugettext('Screenshot')))
    screenshot_link.allow_tags = True
    screenshot_link.label = _('Screenshot')

    def changelist_view(self, request, extra_context=None):
        check_plugins()
        return super(RegisteredPluginAdmin, self).changelist_view(request,
            extra_context)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'is_broken': obj.broken,
        })
        return super(RegisteredItemAdmin, self).render_change_form(request, context, add, change, form_url, obj)


def register(site):
    site.register(RegisteredPlugin, RegisteredPluginAdmin)
