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
import os

from optparse import make_option

from django.conf import settings
from django.core.management.base import CommandError, LabelCommand

from merengue.base.management.base import MerengueCommand
from merengue.utils import save_config


class Command(LabelCommand, MerengueCommand):

    option_list = LabelCommand.option_list + (
        make_option('-o', '--overwrite', action='store_true', dest='overwrite',
                    default=False, help="Overwrite the zip file"),
        make_option('-a', '--all', action='store_true', dest='all',
                    default=False, help="Save all files on file system"),
    )
    help = "Creates a zip file from merengue site configuration"
    args = "[config_name]"
    label = 'config name'
    requires_model_validation = True
    can_import_settings = False

    def handle_label(self, config_name, **options):
        path_zip = os.path.join(settings.BASEDIR, '%s.zip' % config_name)
        overwrite = options['overwrite']
        if not overwrite and os.path.isfile(path_zip):
            raise CommandError("File existing use the --overwrite option or " \
                               "!remove the file %s" % path_zip)
        save_all = options['all']

        file_zip = open(path_zip, 'w')
        buffer_zip = save_config(overwrite, save_all)
        file_zip.write(buffer_zip.getvalue())
