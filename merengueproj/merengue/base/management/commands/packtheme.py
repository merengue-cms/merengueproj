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
import zipfile
from optparse import make_option

from django.conf import settings
from django.core.management.base import CommandError, LabelCommand

from merengue.base.management.base import MerengueCommand


class Command(LabelCommand, MerengueCommand):

    option_list = LabelCommand.option_list + (
        make_option('-o', '--overwrite', action='store_true', dest='overwrite', default=False,
            help="Overwrite the zip file"),
    )
    help = "Creates a zip file from a theme"
    args = "[theme_name]"
    label = 'theme name'
    requires_model_validation = False
    can_import_settings = False

    def handle_label(self, theme_name, **options):
        path_zip = os.path.join(settings.BASEDIR, '%s.zip' % theme_name)

        if not options['overwrite'] and os.path.isfile(path_zip):
            raise CommandError("File existing use packtheme --overwrite or remove the file %s" %path_zip)
        zip_theme = zipfile.ZipFile(path_zip, "w", compression=zipfile.ZIP_DEFLATED)

        path_templates = os.path.join(settings.TEMPLATE_DIRS[0], 'themes', theme_name)
        path_templates_zip = os.path.join(theme_name, 'templates')
        self.add_folder_to_zip(zip_theme, path_project=path_templates, path_zip=path_templates_zip, theme_name=theme_name)

        path_media = os.path.join(settings.MEDIA_ROOT, 'themes', theme_name)
        path_media_zip = os.path.join(theme_name, 'media')
        self.add_folder_to_zip(zip_theme, path_project=path_media, path_zip=path_media_zip, theme_name=theme_name)

        zip_theme.close()
        print 'File created successfully in path %s' % path_zip

    def add_folder_to_zip(self, zip_theme, path_project, path_zip, theme_name):
        for i, (dirpath, dirnames, filenames) in enumerate(os.walk(path_project)):
            if '.svn' in dirnames:
                index_svn = dirnames.index('.svn')
                del dirnames[index_svn]
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                file_path_zip = os.path.join(path_zip, file_path.replace('%s/' % path_project, ''))
                zip_theme.write(file_path, file_path_zip)
