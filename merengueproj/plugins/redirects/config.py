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

from django.contrib.auth.models import User, Group
from merengue.pluggable import Plugin
from merengue.registry import params
from plugins.redirects.models import Redirect
from plugins.redirects.admin import RedirectAdmin
from django.utils.translation import ugettext as _


class PluginConfig(Plugin):
    """
    Redirect Plugin config instance
    """
    name = 'Redirects'
    description = 'Redirects Plugin'
    version = '0.0.1'

    config_params = [
        params.Single(name='review_title',
                      label=_('title for reviewing task'),
                      default=_('Review this redirection')),
        params.List(name="review_users",
                    label=_("Users by default to have redirects reviewed"),
                    choices=[(u.username, u.username) for u in User.objects.all()]),
        params.List(name="review_groups",
                    label=_("User groups by default to have redirects reviewed"),
                    choices=[(g.name, g.name) for g in Group.objects.all()]),
    ]

    def get_middlewares(self):
        return ['plugins.redirects.middleware.RedirectMiddleware']

    def get_model_admins(self):
        return [(Redirect, RedirectAdmin), ]

    def get_perms(self):
        return (
            (_('Submit redirects'), 'submit_redirects', [Redirect], ),
            (_('Manage redirects'), 'manage_redirects', [Redirect], )
        )
