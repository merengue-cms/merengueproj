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

    @classmethod
    def get_category(cls):
        return 'action'

    @classmethod
    def get_url(cls, request):
        raise NotImplementedError()

    @classmethod
    def get_extended_attrs(cls):
        return {'name': cls.name}

    @classmethod
    def get_response(cls):
        raise NotImplementedError()

    @classmethod
    def has_action(cls):
        return True


class SiteAction(BaseAction):

    @classmethod
    def get_url(cls, request):
        return reverse("site_action", args=(cls.name, ))


class UserAction(BaseAction):

    @classmethod
    def has_action(cls, user):
        return super(UserAction, cls).has_action()

    @classmethod
    def get_url(cls, request, user):
        return reverse("user_action", args=(user.username, cls.name, ))


class ContentAction(BaseAction):

    @classmethod
    def get_url(cls, request, content):
        content_type = ContentType.objects.get_for_model(content.__class__)
        return reverse("content_action", args=(content_type.id, content.id, cls.name, ))

    @classmethod
    def get_response(cls, content):
        raise NotImplementedError()

    @classmethod
    def has_action(cls, content):
        return super(ContentAction, cls).has_action()
