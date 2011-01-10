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
            help="Overwrite the theme directories"),
        make_option('-p', '--path', dest='path_zip',
            help="Path of zip file"),
    )
    help = "Unzip a zip file and create a theme"
    args = "[theme_name]"
    label = 'theme name'
    requires_model_validation = False
    can_import_settings = False

    def handle_label(self, theme_name, **options):
        path_templates = os.path.join(settings.TEMPLATE_DIRS[0], 'themes', theme_name)
        path_media = os.path.join(settings.MEDIA_ROOT, 'themes', theme_name)

        if not options['overwrite'] and (os.path.isdir(path_templates) or os.path.isdir(path_media)):
            if os.path.isdir(path_templates) and os.path.isdir(path_media):
                raise CommandError("Directories existing use unpacktheme --overwrite or remove the directories %s and %s" % (path_templates, path_media))
            elif os.path.isdir(path_templates):
                raise CommandError("Directory existing use unpacktheme --overwrite or remove the directory %s" % path_templates)
            elif os.path.isdir(path_media):
                raise CommandError("Directory existing use unpacktheme --overwrite or remove the directory %s" % path_media)

        path_zip = options.get('path_zip', None) or settings.BASEDIR
        path_zip = os.path.join(path_zip, '%s.zip' % theme_name)
        zip_theme = zipfile.ZipFile(path_zip)

        path_general_templates = settings.TEMPLATE_DIRS[0]
        subdirectories_path_templates = os.path.join('themes', theme_name)
        path_templates = os.path.join(path_general_templates, subdirectories_path_templates)
        self.create_tree(path_general_templates, subdirectories_path_templates.split('/'))
        path_templates_zip = os.path.join(theme_name, 'templates/')
        self.unzip_folder(zip_theme, path_project=path_templates, path_zip=path_templates_zip, theme_name=theme_name)

        path_general_media = settings.MEDIA_ROOT
        subdirectories_path_media = os.path.join('themes', theme_name)
        path_media = os.path.join(path_general_media, subdirectories_path_media)
        self.create_tree(path_general_media, subdirectories_path_media.split('/'))
        path_media_zip = os.path.join(theme_name, 'media/')
        self.unzip_folder(zip_theme, path_project=path_media, path_zip=path_media_zip, theme_name=theme_name)

        zip_theme.close()
        print 'Unzip successfully'

    def unzip_folder(self, zip_theme, path_project, path_zip, theme_name):
        for name in zip_theme.namelist():
            if path_zip in name:
                name_without_path_zip = name.replace(path_zip, '')
                subdirectories = name_without_path_zip.split('/')
                self.create_tree(path_project, subdirectories[:-1])
                outfile = open(os.path.join(path_project, name_without_path_zip), 'wb')
                outfile.write(zip_theme.read(name))
                outfile.close()

    def create_tree(self, path_general, subdirectories):
        subdirectory_path = ''
        for subdirectory in subdirectories:
            if not subdirectory:
                continue
            subdirectory_path = os.path.join(path_general, subdirectory_path, subdirectory)
            self.create_directory(subdirectory_path)

    def create_directory(self, subdirectory_path):
        if not os.path.isdir(subdirectory_path):
            os.mkdir(subdirectory_path)
