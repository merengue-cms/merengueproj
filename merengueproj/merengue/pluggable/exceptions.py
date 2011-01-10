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


class BrokenPlugin(Exception):

    def __init__(self, plugin_dir, exc_type, exc_value, tb):
        super(BrokenPlugin, self).__init__()
        self.plugin_dir = plugin_dir
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.traceback = tb

    def __unicode__(self):
        return u'Broken plugin %s' % self.plugin_dir
