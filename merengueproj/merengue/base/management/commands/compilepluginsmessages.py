# Copyright (c) 2010 by Yaco Sistemas <jcorrea@yaco.es>
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

import os
from optparse import make_option

from django.conf import settings
from django.core.management import call_command

from merengue.base.management.base import MerengueCommand
from merengue.pluggable.utils import get_plugins_dir


class Command(MerengueCommand):
    help = "Generate translation for plugins"

    option_list = MerengueCommand.option_list + (
        make_option('-p', '--plugin', default=None, dest='plugin',
                    help='Directory plugin'),
                   )

    def compilepluginmessages(self, dirname, plugin_dir):
        if os.path.isdir(os.path.join(dirname, plugin_dir)) and os.path.isdir(os.path.join(dirname, plugin_dir, 'locale')):
            print 'Compiling messages for plugin %s' % plugin_dir
            langtrans = os.listdir(os.path.join(dirname, plugin_dir, 'locale'))
            os.chdir(os.path.join(dirname, plugin_dir)) #change current directory to make plugin messages
            call_command('compilemessages') #call makemessages command to search new translations
        else:
            print '%s isn\'t a plugin or it doesn\'t have a \"locale\" directory.' %(plugin_dir)

    def handle(self, **options):
        dirname = os.path.join(settings.BASEDIR, get_plugins_dir())
        plugin_dir = options.get('plugin', None)
        if plugin_dir:
            self.compilepluginmessages(dirname, plugin_dir)
        else:
            for plugin_dir in os.listdir(dirname):
                self.compilepluginmessages(dirname, plugin_dir)
