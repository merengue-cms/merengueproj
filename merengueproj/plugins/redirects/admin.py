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

from merengue.base.admin import PluginAdmin
from plugins.redirects.models import Redirect
from merengue.perms.utils import has_global_permission


class RedirectAdmin(PluginAdmin):
    """
    ModelAdmin for Redirect plugin.
    """

    def has_add_permission(self, request):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        user = request.user
        return has_global_permission(user, 'submit_redirects') or \
                                has_global_permission(user, 'manage_redirects')

    def has_change_permission(self, request, obj=None):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        if obj and obj.is_active != bool(request.POST.get('is_active')):
            return has_global_permission(request.user, 'manage_redirects')
        return super(RedirectAdmin, self).has_change_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super(RedirectAdmin, self).get_form(request, obj, **kwargs)
        if not has_global_permission(request.user, 'manage_redirects'):
            # only redirects managers can activate a redirect
            del form.base_fields['is_active']
        return form

    def save_model(self, request, obj, form, change):
        from plugins.redirects.utils import create_redirect_review_task
        saved = super(RedirectAdmin, self).save_model(request, obj, form, change)
        if not change:
            create_redirect_review_task(request.user, obj)
        return saved


def register(site):
    """ Merengue admin registration callback """
    site.register(Redirect, RedirectAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Redirect)
