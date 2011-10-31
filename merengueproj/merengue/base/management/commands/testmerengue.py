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

# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management import call_command

from merengue.base.management.base import MerengueCommand


class Command(MerengueCommand):
    help = "Executes all the test in APPS_TO_TEST setting"

    def handle(self, **options):
        for app in settings.APPS_TO_TEST:
            print '\nTesting %r application...\n' % app
            call_command('test', app)
