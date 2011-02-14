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
from merengue.base.admin import BaseAdmin, set_field_read_only
from merengue.perms import utils as perms_api
from merengue.theming.checker import check_themes
from merengue.theming.models import Theme


class ThemeAdmin(BaseAdmin):
    readonly_fields = ('name', 'description', 'directory_name', 'installed')
    list_display = ('name', 'active', 'directory_name', 'admin_thumbnail', )
    actions = None

    def admin_thumbnail(self, instance):
        if instance.preview:
            return u'<a href="%s"><img src="%s" alt="Theme screenshot" /></a>' % \
                        (instance.preview, instance.preview)
        return instance
    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    def get_form(self, request, obj=None):
        form = super(ThemeAdmin, self).get_form(request, obj)
        if not obj.installed:
            set_field_read_only(form.base_fields['active'], 'active', obj)
        return form

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return perms_api.can_manage_site(request.user)

    def changelist_view(self, request, extra_context=None):
        check_themes()
        return super(ThemeAdmin, self).changelist_view(request, extra_context)


def register(site):
    site.register(Theme, ThemeAdmin)
