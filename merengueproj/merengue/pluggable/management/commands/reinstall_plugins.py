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

from merengue.base.management.base import MerengueCommand
from merengue.pluggable.loading import load_plugins
from merengue.pluggable.models import RegisteredPlugin
from merengue.pluggable.utils import install_plugin


class Command(MerengueCommand):
    help = "Disable and enable all actives plugins"
    args = ""

    def handle(self, app=None, target=None, **options):
        load_plugins()
        plugins = RegisteredPlugin.objects.actives()
        for plugin_registered in plugins:
            print 'Reactivating plugin %s...' % plugin_registered.directory_name
            install_plugin(plugin_registered)
