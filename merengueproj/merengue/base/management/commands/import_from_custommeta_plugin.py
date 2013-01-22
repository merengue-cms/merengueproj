# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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

import sys


from django.core.management.base import BaseCommand

from merengue.pluggable.utils import get_plugin


class Command(BaseCommand):

    def handle(self, *args, **options):
        old_plugin = get_plugin('custommeta')
        old_plugin = old_plugin and old_plugin.get_registered_item()
        if not old_plugin or not old_plugin.installed:
            print "Old custommeta plugin is not installed. Nothing to do!"
            return
        if not old_plugin.active:
            print "Old custommeta plugin is installed but is not active. Nothing to do!"
            return
        from plugins.custommeta.models import CustomMeta as OldCustomMeta
        from plugins.core.models import CustomMeta

        old_objects = OldCustomMeta.objects.all()
        total = old_objects.count()

        print ('Importing %s old custommeta objects' % total)
        index = 1
        for i in old_objects:
            sys.stdout.write('CustomMeta object [%s/%s]\r' % (index, total))
            sys.stdout.flush()
            CustomMeta.objects.get_or_create(
                url_regexp=i.url_regexp,
                title=i.title,
                description=i.description,
                keywords=i.keywords)
            index += 1
        print '\nDone'
