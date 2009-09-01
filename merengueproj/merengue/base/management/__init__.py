import os
import sys

from django.core import management as django_management

from merengue.base.management.base import MerengueCommand


# cache of loaded Merengue commands
_merengue_commands = None


def get_commands():
    """
    Like django.core.management.get_commands but filters only merengue
    management commands (commands extending MerengueCommand)

    """
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

    def main_help_text(self):
        """
        Returns the script's main help text, as a string.
        """
        usage = ['', "Type '%s help <subcommand>' for help on a specific subcommand." % self.prog_name, '']
        usage.append('Available merengue commands:')
        commands = get_commands().keys()
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
            app_name = get_commands()[subcommand]
            if isinstance(app_name, MerengueCommand):
                # If the command is already loaded, use it directly.
                klass = app_name
            else:
                klass = django_management.load_command_class(app_name, subcommand)
        except KeyError:
            sys.stderr.write("Unknown command: %r\nType '%s help' for usage.\n" % \
                (subcommand, self.prog_name))
            sys.exit(1)
        return klass


def execute_from_command_line(argv=None):
    """
    A simple method that runs a ManagementUtility.
    """
    utility = ManagementUtility(argv)
    utility.execute()
