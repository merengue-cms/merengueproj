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
import sys

from django.core import management as django_management
from django.core.management.base import BaseCommand, handle_default_options

from merengue.base.management.base import MerengueCommand  # pyflakes:ignore

# cache of loaded Merengue commands
_merengue_commands = None


def get_commands(only_merengue_commands=False):
    """
    Like django.core.management.get_commands but filters only merengue
    management commands (commands extending MerengueCommand) if only_merengue_commands
    is True
    """
    if not only_merengue_commands:
        return django_management.get_commands()
    global _merengue_commands
    if _merengue_commands is None:
        _merengue_commands = {}
        # look for commands into every merengue app
        merengue_dir = os.path.abspath(os.path.join(__path__[0], '..', '..'))
        for f in os.listdir(merengue_dir):
            path = os.path.join(merengue_dir, f, 'management')
            if os.path.isdir(path):
                commands = django_management.find_commands(os.path.abspath(path))
                for command in commands:
                    _merengue_commands[command] = 'merengue.%s' % f
    return _merengue_commands


class ManagementUtility(django_management.ManagementUtility):
    """
    Based on django.core.management.ManagementUtility, modified for considering
    only MerengueCommands.
    """

    def __init__(self, argv=None, only_merengue_commands=False):
        super(ManagementUtility, self).__init__(argv)
        self.only_merengue_commands = only_merengue_commands

    def main_help_text(self):
        """
        Returns the script's main help text, as a string.
        """
        usage = ['', "Type '%s help <subcommand>' for help on a specific subcommand." % self.prog_name, '']
        usage.append('Available merengue commands:')
        commands = get_commands(self.only_merengue_commands).keys()
        commands.sort()
        for cmd in commands:
            usage.append('  %s' % cmd)
        return '\n'.join(usage)

    def fetch_command(self, subcommand):
        """
        Tries to fetch the given subcommand, printing a message with the
        appropriate command called from the command line ("merengue-admin.py")
        if it can't be found.

        """
        try:
            app_name = get_commands(self.only_merengue_commands)[subcommand]
            if isinstance(app_name, BaseCommand):
                # If the command is already loaded, use it directly.
                klass = app_name
            else:
                klass = django_management.load_command_class(app_name, subcommand)
        except KeyError:
            sys.stderr.write("Unknown command: %r\nType '%s help' for usage.\n" % \
                (subcommand, self.prog_name))
            sys.exit(1)
        return klass

    def execute(self):
        """
        Given the command-line arguments, this figures out which subcommand is
        being run, creates a parser appropriate to that command, and runs it.

        Taken from django execute method, but enabling all active plugins
        before execution.
        """
        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the commands that are available, so they
        # must be processed early.
        parser = django_management.LaxOptionParser(usage="%prog subcommand [options] [args]",
                                 version=django_management.get_version(),
                                 option_list=BaseCommand.option_list)
        try:
            options, args = parser.parse_args(self.argv)
            handle_default_options(options)
        except:
            pass  # Ignore any option errors at this point.

        try:
            subcommand = self.argv[1]
        except IndexError:
            sys.stderr.write("Type '%s help' for usage.\n" % self.prog_name)
            sys.exit(1)

        if subcommand == 'help':
            if len(args) > 2:
                self.fetch_command(args[2]).print_help(self.prog_name, args[2])
            else:
                parser.print_lax_help()
                sys.stderr.write(self.main_help_text() + '\n')
                sys.exit(1)
        # Special-cases: We want 'django-admin.py --version' and
        # 'django-admin.py --help' to work, for backwards compatibility.
        elif self.argv[1:] == ['--version']:
            # LaxOptionParser already takes care of printing the version.
            pass
        elif self.argv[1:] == ['--help']:
            parser.print_lax_help()
            sys.stderr.write(self.main_help_text() + '\n')
        else:
            command = self.fetch_command(subcommand)
            if subcommand not in ['migrate', 'syncdb', 'startproject', 'dbshell',
                                  'rebuild_db', 'restore_config', 'schemamigration',
                                  'datamigration', 'backupdb', 'startplugin']:
                # This is override fragment of Django execute method
                # only works if models have been created (not with syncdb, startproject neither migrate)
                from merengue.pluggable import enable_active_plugins
                enable_active_plugins()
            command.run_from_argv(self.argv)


def execute_from_command_line(argv=None):
    """
    A simple method that runs a ManagementUtility (merengue-admin.py)

    Only we can call merengue commands (not all django ones)
    """
    utility = ManagementUtility(argv, only_merengue_commands=True)
    utility.execute()


def execute_manager(settings_mod, argv=None):
    """
    Like execute_from_command_line(), but for use by manage.py, a
    project-specific django-admin.py utility.

    In this case we can call every django command (not only merengue ones)
    """
    django_management.setup_environ(settings_mod)
    utility = ManagementUtility(argv, only_merengue_commands=False)
    utility.execute()
