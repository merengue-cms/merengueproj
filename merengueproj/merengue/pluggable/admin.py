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
from merengue.pluggable.utils import has_required_dependencies, install_plugin
from merengue.registry.admin import RegisteredItemAdmin


class RegisteredPluginAdmin(RegisteredItemAdmin):
    change_form_template = 'admin/plugin/plugin_change_form.html'
    change_list_template = 'admin/plugin/plugin_change_list.html'
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name',
        'description', 'version', 'directory_name', )
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

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(RegisteredPluginAdmin, self).get_readonly_fields(request, obj)
        if obj.directory_name in settings.REQUIRED_PLUGINS:
            # required plugins cannot being deactivated or uninstalled
            readonly_fields += ('active', 'installed', )
        elif not obj.installed:
            readonly_fields += ('active', )

        return readonly_fields

    def get_form(self, request, obj=None):
        form = super(RegisteredPluginAdmin, self).get_form(request, obj)
        if not has_required_dependencies(obj):
            installed_field = form.base_fields['installed']
            help_text = installed_field.help_text
            installed_field.help_text = "%s %s" \
                                        % (help_text,
                                          _('Not all dependencies are met'))
        if obj.broken:
            # a broken registered item will be not editable by anybody
            for field_name, field in form.base_fields.items():
                set_field_read_only(field, field_name, obj)
        return form

    def save_form(self, request, form, change):
        change_installed_field = 'installed' in form.changed_data
        if 'installed' in form.cleaned_data:
            is_installed = form.cleaned_data['installed'] == True
        registered_plugin = form.save(commit=False)
        if change_installed_field and is_installed:
            registered_plugin.active = True
            install_plugin(registered_plugin)
        return registered_plugin

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
