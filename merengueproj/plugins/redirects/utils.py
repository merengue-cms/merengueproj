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

from django.utils.translation import ugettext_lazy as _

from merengue.review import create_review_task
from merengue.pluggable.utils import get_plugin
from django.contrib.auth.models import User, Group


def create_redirect_review_task(user, obj):
    config = get_plugin('redirects').get_config()
    usernames = config.get('review_users', []).get_value()
    groupnames = config.get('review_groups', []).get_value()
    create_review_task(user,
        title=config['review_title'].value or _('Review this redirection'),
        url=obj.old_path,
        task_object=obj,
        users=[u for u in User.objects.filter(username__in=usernames)],
        groups=[g for g in Group.objects.filter(name__in=groupnames)])
