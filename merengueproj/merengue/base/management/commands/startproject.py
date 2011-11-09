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
from random import choice

from django.core.management.base import CommandError, LabelCommand
from django.utils.importlib import import_module

from merengue.base.management.base import MerengueCommand, copy_helper


class Command(LabelCommand, MerengueCommand):
    """Based on django.core.management.commands.starproject, but handling the
    copy of the skeleton project differently."""
    option_list = LabelCommand.option_list + (
        make_option('-d', '--copy', action='store_false', dest='symlink', default=True,
            help="Copy Merengue instead of link."),
    )
    help = "Creates a Merengue project directory structure for the given project name in the current directory."
    args = "[projectname]"
    label = 'project name'
    requires_model_validation = False
    can_import_settings = False

    def handle_label(self, project_name, **options):
        # Determine the project_name a bit naively -- by looking at the name of
        # the parent directory.
        directory = os.getcwd()

        # Check that the project_name cannot be imported.
        try:
            import_module(project_name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an existing Python module and cannot be used as a project name. Please try another name." % project_name)

        copy_helper(self.style, project_name, directory, symlink=options['symlink'])

        # Create a random SECRET_KEY hash, and put it in the main settings.
        main_settings_file = os.path.join(directory, project_name, 'settings.py')
        settings_contents = open(main_settings_file, 'r').read()
        fp = open(main_settings_file, 'w')
        secret_key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
        settings_contents = re.sub(r"(?<=SECRET_KEY = ')'", secret_key + "'", settings_contents)
        fp.write(settings_contents)
        fp.close()
