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
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import UserAction, SiteAction, ContentAction
from merengue.base.utils import get_login_url
from merengue.section.models import BaseSection
from merengue.registry.items import ContentTypeFilterProvider


class AdminAction(UserAction):
    name = 'admin'
    verbose_name = _('Admin site')

    def get_url(self, request, user):
        return reverse('admin_index')

    def has_action(self, request, user):
        return user.is_staff


class LoginAction(UserAction):
    name = 'login'
    verbose_name = _('Login')
    login_view = 'merengue_login'

    def get_url(self, request, user):
        login_url = get_login_url()
        if request.get_full_path() not in [reverse(self.login_view), reverse('admin:logout')]:  # to avoid automatic logout after login
            login_url += '?next=%s' % request.get_full_path()
        return login_url

    def has_action(self, request, user):
        return not user.is_authenticated()


class LogoutAction(UserAction):
    name = 'logout'
    verbose_name = _('Logout')
    logout_view = 'merengue_logout'

    def get_url(self, request, user):
        merengue_logout_url = reverse(self.logout_view)
        logout_redirect_url = settings.LOGOUT_REDIRECT_URL
        if logout_redirect_url:
            merengue_logout_url = '%s?next=%s' % (merengue_logout_url, logout_redirect_url)
        return merengue_logout_url

    def has_action(self, request, user):
        return user.is_authenticated()


class PrintAction(SiteAction):
    name = 'print'
    verbose_name = _('Print')


class HotLinkAction(ContentTypeFilterProvider, ContentAction):
    name = 'hotlink'
    verbose_name = _('Link to your section')
    active_by_default = False

    def get_url(self, request, content):
        return reverse('hotlink', args=(content.pk,))

    def has_action(self, request, content):
        user = request.user
        if user.is_anonymous():
            return False
        if not self.match_type(content):
            return False
        if user.is_superuser:
            return True
        class_names = ['basesection']
        subclasses = BaseSection.get_subclasses()
        class_names += [subclass.__name__.lower() for subclass in subclasses]
        return user.contents_owned.filter(class_name__in=class_names).exists()
