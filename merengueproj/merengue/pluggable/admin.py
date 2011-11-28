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
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.functional import update_wrapper
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from cmsutils.log import send_info

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
    list_filter = ('installed', 'active', 'broken', )

    fieldsets = (
        ('',
            {'fields': ('name', 'description', 'version', 'directory_name',
                        'module', 'class_name', 'required_apps',
                        'required_plugins', ), }
        ),
        (_('Status'),
            {'fields': ('installed', 'active', 'config'), },
        )
    )

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):

            def wrapper(*args, **kwargs):
                #kwargs['model_admin'] = self
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urls = super(RegisteredPluginAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^register-new-plugins/$', wrap(self.register_new_plugins),
                name='register_plugins'))
        return my_urls + urls

    def register_new_plugins(self, request, extra_context=None):
        check_plugins(force_detect=True, force_broken_detect=True)
        send_info(request, _('Plugins detections done'))
        return HttpResponseRedirect('..')

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
        if change_installed_field:
            if is_installed:
                registered_plugin.active = True
                install_plugin(registered_plugin)
            else:
                registered_plugin.active = False
        return registered_plugin

    def object_tools(self, request, mode, url_prefix):
        tools = super(RegisteredPluginAdmin, self).object_tools(request, mode, url_prefix)
        if mode == 'list':
            tools = [{'url': url_prefix + 'register-new-plugins/', 'label': ugettext('Detect new plugins'), 'class': 'default', 'permission': 'change'}] + tools
        return tools

    def has_add_permission(self, request):
        return False

    def screenshot_link(self, obj):
        if not obj.screenshot:
            return ugettext('None')
        return mark_safe(u'<a href="%s" target="_blank">%s</a>' % (obj.screenshot, ugettext('Screenshot')))
    screenshot_link.allow_tags = True
    screenshot_link.short_description = _('Screenshot')

    def changelist_view(self, request, extra_context=None):
        check_plugins()
        if RegisteredPlugin.objects.all().count() == len(settings.REQUIRED_PLUGINS):
            messages.warning(request, _('You have not registered all the plugins. Click <a href="%(url)s">here</a> in order to register them') %
                             {'url': reverse('admin:register_plugins')})
        return super(RegisteredPluginAdmin, self).changelist_view(request,
            extra_context)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'is_broken': obj.broken,
            'required_and_not_installed': obj.directory_name in settings.REQUIRED_PLUGINS and not obj.installed,
        })
        return super(RegisteredItemAdmin, self).render_change_form(request, context, add, change, form_url, obj)


def register(site):
    site.register(RegisteredPlugin, RegisteredPluginAdmin)
