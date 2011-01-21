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
from plugins.redirects.config import PluginConfig
from django.contrib.auth.models import User, Group


def create_redirect_review_task(user, obj):
    config = PluginConfig.get_config()
    user_ids = config['review_users'].value
    group_ids = config['review_groups'].value
    create_review_task(user,
        title=config['review_title'].value or _('Review this redirection'),
        url=obj.old_path,
        task_object=obj,
        users=[u for u in User.objects.filter(id__in=user_ids)],
        groups=[g for g in Group.objects.filter(id__in=group_ids)])
