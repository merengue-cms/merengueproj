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

import os
import re
from optparse import make_option

from django.conf import settings
from django.core.management.base import CommandError, LabelCommand
from django.utils.importlib import import_module

from merengue.base.management.base import MerengueCommand, copy_dir

plugin_re = re.compile(r'^[_\w]+$')


def do_file_replacements(file_path, plugin_name):
    contents = open(file_path, 'r').read()
    fp = open(file_path, 'w')
    contents = contents.replace('fooplugin', plugin_name)
    contents = contents.replace('FooModel', '%sModel' % plugin_name.capitalize())
    contents = contents.replace('foomodel', '%smodel' % plugin_name)
    contents = contents.replace('FooBlock', '%sBlock' % plugin_name.capitalize())
    contents = contents.replace('fooblock', '%sblock' % plugin_name)
    contents = contents.replace('foo_block', '%s_block' % plugin_name)
    contents = contents.replace('Foo block', '%s block' % plugin_name.capitalize())
    contents = contents.replace('FooAction', '%sAction' % plugin_name.capitalize())
    contents = contents.replace('Foo action', '%s action' % plugin_name.capitalize())
    contents = contents.replace('fooaction', '%saction' % plugin_name)
    contents = contents.replace('foo_list', '%s_list' % plugin_name)
    contents = contents.replace('Foo listing', '%s listing' % plugin_name.capitalize())
    contents = contents.replace('foo items', '%s items' % plugin_name)
    contents = contents.replace('Foo plugin', '%s plugin' % plugin_name.capitalize())
    contents = contents.replace('Foo panel', '%s panel' % plugin_name.capitalize())
    contents = contents.replace('foo_panel', '%s_panel' % plugin_name)
    fp.write(contents)
    fp.close()


class Command(LabelCommand, MerengueCommand):
    """Based on django.core.management.commands.startproject, but handling the
    copy of the skeleton project differently."""
    option_list = LabelCommand.option_list + (
        make_option('-d', '--develop', action='store_true', dest='develop',
            help="For development of Merengue's core, symlink instead of copy."),
    )
    help = "Creates a Merengue plugin directory structure for the given plugin name in the plugins directory."
    args = "[pluginname]"
    label = 'plugin name'
    requires_model_validation = False

    def handle_label(self, plugin_name, **options):

        if plugin_name != plugin_name.lower():
            raise CommandError("%r is not a Pythonic plugin name. It should be a lowercase word." % plugin_name)
        if not plugin_re.match(plugin_name):
            raise CommandError("%r should contain only letters, numbers and underscores." % plugin_name)

        plugin_directory = os.path.join(os.getcwd(), settings.PLUGINS_DIR, plugin_name)
        merengue_root = settings.MERENGUEDIR
        skel_directory = os.path.join(merengue_root, 'skel', 'plugin')

        # Check that the plugin_name cannot be imported.
        try:
            import_module('plugins.%s' % plugin_name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an existing plugin and cannot be used as an plugin name. Please try another name." % plugin_name)

        copy_dir(skel_directory, plugin_directory, plugin_name, False, self.style)

        for parent, directories, files in os.walk(plugin_directory):
            for filename in files:
                file_path = os.path.join(plugin_directory, parent, filename)
                if filename.endswith('.py') or filename.endswith('.html') or filename.endswith('.css'):
                    do_file_replacements(file_path, plugin_name)
            for path_name in directories + files:
                path = os.path.join(plugin_directory, parent, path_name)
                for replacement in ('fooplugin', 'foo', ):
                    if replacement in path_name:
                        new_path_name = path_name.replace(replacement, plugin_name)
                        new_path = os.path.join(plugin_directory, parent, new_path_name)
                        os.rename(path, new_path)
                        if path_name in directories:
                            directories.append(new_path_name)  # make sure we will recurse into the directory
                        path = new_path
                        break  # only do one replacement
        print 'Created %r plugin in %s' % (plugin_name, plugin_directory)
