# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.contrib.auth.models import User
from merengue.review.models import ReviewTask


def create_review_task(owner, title=None, url=None, task_object=None, users=[], groups=[]):
    if groups:
        for user in User.objects.filter(groups__in=groups):
            if user not in users:
                users.append(user)

    rt = ReviewTask()
    rt.owner = owner
    rt.title = title
    rt.task_object = task_object
    rt.url = url
    rt.save()

    for user in users:
        rt.assigned_to.add(user)


def get_publishers(content):
    """ Get users who may publish a content """
    from merengue.perms import utils as perms_api
    return [u for u in User.objects.filter(is_staff=True) if perms_api.has_permission(content, u, 'can_published')]


def get_review_tasks(**filters):
    return ReviewTask.objects.filter(**filters)
