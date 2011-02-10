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

from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from merengue.action import get_action


def site_action(request, name):
    action_item = get_action(name=name)
    item_class = action_item.get_registry_item()
    return item_class.get_response(request)


def content_action(request, content_type_id, object_id, name):
    action_item = get_action(name=name)
    item_class = action_item.get_registry_item()
    try:
        content_type = ContentType.objects.get(pk=content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        raise Http404("Content type %s object %s doesn't exist" % (content_type_id, object_id))
    if hasattr(obj, 'get_real_instance'):
        obj = obj.get_real_instance()
    return item_class.get_response(request, obj)


def user_action(request, username, name):
    action_item = get_action(name=name)
    item_class = action_item.get_registry_item()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User %s doesn't exist" % username)
    return item_class.get_response(request, user)
