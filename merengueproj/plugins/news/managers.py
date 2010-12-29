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

from cmsutils.managers import ActiveManager

from merengue.base.managers import BaseContentManager


class NewsItemManager(ActiveManager, BaseContentManager):
    """ Show only published and not expired news items """

    def __init__(self):
        super(NewsItemManager, self).__init__(from_date='publish_date', to_date='expire_date')

    def actives(self):
        return super(NewsItemManager, self).actives().filter(status='published')

    def allpublished(self):
        return self.filter(status='published')

    def published(self):
        return self.actives().filter(status='published')
