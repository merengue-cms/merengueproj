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

"""
Overridden south syncdb command
"""

from django.core.management.base import NoArgsCommand
from django.core.management import call_command

# Try south syncdb, if not installed fail back to django syncdb
try:
    from south.management.commands import syncdb
except ImportError:
    from django.core.management.commands import syncdb


class Command(NoArgsCommand):
    option_list = syncdb.Command.option_list
    help = syncdb.Command.help

    def handle_noargs(self, migrate_all=False, **options):
        # OK, run the original syncdb
        syncdb.Command().execute(**options)

        # Plugin registration
        verbosity = int(options.get('verbosity', 0))

        if verbosity:
            print '\nRegistering plugins:'
        call_command('register_new_plugins')
        if verbosity:
            print '  [DONE]'
