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

from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from merengue.action.models import RegisteredAction
from merengue.registry.items import RegistrableItem


class BaseAction(RegistrableItem):
    model = RegisteredAction
    singleton = True

    @classmethod
    def get_category(cls):
        return 'action'

    @classmethod
    def get_extended_attrs(cls):
        return {'name': cls.name}

    def get_url(self, request):
        raise NotImplementedError()

    def get_response(self, request):
        raise NotImplementedError()

    def has_action(self, request):
        return True


class SiteAction(BaseAction):

    def get_url(self, request):
        return reverse("site_action", args=(self.name, ))


class UserAction(BaseAction):

    def has_action(self, request, user):
        return super(UserAction, self).has_action(request)

    def get_url(self, request, user):
        return reverse("user_action", args=(user.username, self.name, ))


class ContentAction(BaseAction):

    def get_url(self, request, content):
        content_type = ContentType.objects.get_for_model(content.__class__)
        return reverse("content_action", args=(content_type.id, content.id, self.name, ))

    def get_response(self, request, content):
        raise NotImplementedError()

    def has_action(self, request, content):
        return super(ContentAction, self).has_action(request)
