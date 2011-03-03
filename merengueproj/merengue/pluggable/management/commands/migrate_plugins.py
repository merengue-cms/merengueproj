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

from django.core.management import call_command

from south.management.commands import migrate

from merengue.utils import ask_yesno_question
from merengue.base.management.base import MerengueCommand
from merengue.pluggable.loading import load_plugins
from merengue.pluggable.models import RegisteredPlugin
from merengue.pluggable.utils import have_south


class Command(MerengueCommand):
    help = "Migrate with south all enabled plugins"
    option_list = migrate.Command.option_list
    args = "[pluginname] [migrationname|zero] [--all] [--list] [--skip] [--merge] [--no-initial-data] [--fake] [--db-dry-run] [--database=dbalias]"

    def handle(self, app=None, target=None, **options):
        load_plugins()
        plugins = RegisteredPlugin.objects.actives()
        if app:
            plugins = plugins.filter(directory_name=app)
            if not plugins:
                print 'Enabled plugin named "%s" does not exist' % app
                return

        for plugin_registered in plugins:
            app_name = plugin_registered.directory_name
            try:
                if have_south(app_name):
                    call_command('migrate', app=app_name, target=target, **options)
            except:
                if ask_yesno_question('The migration of %s plugin has failed... Continue?' % app_name, 'yes'):
                    continue
                raise
