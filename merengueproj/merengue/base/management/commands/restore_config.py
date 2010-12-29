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
import zipfile

from django.core.management.base import CommandError, LabelCommand
from merengue.base.management.base import MerengueCommand
from merengue.utils import restore_config


class Command(LabelCommand, MerengueCommand):

    option_list = LabelCommand.option_list
    help = "Restore merengue site configuration from a zip file"
    args = "[config_name]"
    label = 'config name'
    requires_model_validation = True
    can_import_settings = False

    def handle_label(self, config_name, **options):
        if (not os.path.isfile(config_name) or
            not zipfile.is_zipfile(config_name)):
            raise CommandError("No such zip file \"%s\"" % config_name)
        try:
            zip_config = zipfile.ZipFile(config_name, "r",
                                         compression=zipfile.ZIP_DEFLATED)
        except zipfile.BadZipFile, zipfile.LargeZipFile:
            raise CommandError("Bad or too large zip file \"%s\"" \
                               % config_name)
        restore_config(zip_config)
