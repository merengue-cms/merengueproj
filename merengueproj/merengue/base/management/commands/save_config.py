# -*- coding: utf-8 -*-
import ConfigParser
import os
import StringIO
import zipfile
from optparse import make_option

from django.db.models import get_models
from django.db.models.loading import load_app
from django.conf import settings
from django.core import serializers
from django.core.management.base import CommandError, LabelCommand
from django.utils.encoding import smart_str

from merengue.action.models import RegisteredAction
from merengue.block.models import RegisteredBlock
from merengue.base.management.base import MerengueCommand
from merengue.plugins.models import RegisteredPlugin
from merengue.plugins.utils import get_plugin_module_name
from merengue.themes.models import Theme


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
    requires_model_validation = False
    can_import_settings = False

    def handle_label(self, config_name, **options):
        path_zip = os.path.join(settings.BASEDIR, '%s.zip' % config_name)
        if not options['overwrite'] and os.path.isfile(path_zip):
            raise CommandError("File existing use the --overwrite option or " \
                               "!remove the file %s" % path_zip)
        save_all = options['all']
        zip_config = zipfile.ZipFile(path_zip, "w",
                                     compression=zipfile.ZIP_DEFLATED)
        models_to_save = (
            (RegisteredAction, "actions"),
            (RegisteredBlock, "blocks"),
            (RegisteredPlugin, "plugins"),
            (Theme, "themes"),
        )
        self.add_models(zip_config, models_to_save)
        self.add_plugins(zip_config, path_zip, save_all=save_all)
        self.add_config(zip_config, path_zip, save_all=save_all)
        if save_all:
            self.add_theme(zip_config, path_zip)
        zip_config.close()
        print 'File created successfully in path %s' % path_zip

    def add_models(self, zip_config, models_to_save):
        """
        Add models in tuple of tuples models_to_save
        (ModelClass, "file_name")
        """
        for model_to_save in models_to_save:
            model = model_to_save[0]
            file_name = model_to_save[1]
            fixtures = self.get_fixtures(model)
            format = 'json'
            fixtures_file = "%s.%s" % (file_name, format)
            zip_config.writestr(fixtures_file, "\n".join(fixtures))

    def add_theme(self, zip_config, path_zip):
        """
        Add all data themes related. The save_config argument sets if
        all data is saved or only fixtures.
        """
        themes = Theme.objects.filter(active=True)
        for theme in themes:
            theme_path = theme.get_path()
            theme_path_zip = os.path.join("themes", theme.directory_name)
            self.add_folder(zip_config, theme_path, theme_path_zip)

    def add_plugins(self, zip_config, path_zip, save_all=False):
        """
        Add all data plugins related. The save_config argument sets if
        all data is saved or only fixtures.
        """
        plugins = RegisteredPlugin.objects.filter(installed=True)
        for plugin in plugins:
            plugin_path = plugin.get_path()
            plugin_path_zip = os.path.join("plugins", plugin.directory_name)
            if save_all:
                self.add_folder(zip_config, plugin_path, plugin_path_zip)
            self.add_fixtures(zip_config, plugin, plugin_path, plugin_path_zip)

    def add_config(self, zip_config, path_zip, save_all=False):
        """
        Add a config file according to RFC 822
        http://tools.ietf.org/html/rfc822.html
        """
        config = ConfigParser.ConfigParser()
        main_section = u"main"
        mode = save_all and u"all" or u"fixtures"
        config.add_section(main_section)
        config.set(main_section, u"version", u"MERENGUE_VERSION")
        config.set(main_section, u"mode", mode)
        config_string = StringIO.StringIO()
        config.write(config_string)
        zip_config.writestr('config.ini', config_string.getvalue())
        config_string.close()

    def add_fixtures(self, zip_config, plugin, plugin_path, plugin_path_zip):
        """
        Backup fixtures into zip file
        """
        # next two sentences is for avoiding problems with zipfile module
        # (encoding errors)
        plugin_path = smart_str(plugin_path)
        plugin_path_zip = smart_str(plugin_path_zip)
        plugin_modname = get_plugin_module_name(plugin.directory_name)
        plugin_mod = load_app(plugin_modname)
        plugin_models = get_models(plugin_mod)
        fixtures = self.get_fixtures(plugin_models)
        format = 'json'
        fixtures_file = os.path.join(plugin_path_zip, "fixtures.%s" % format)
        zip_config.writestr(fixtures_file, "\n".join(fixtures))

    def get_fixtures(self, model_or_models, format='json'):
        data = []
        format = format.lower()
        if not isinstance(model_or_models, (list, tuple)):
            models_list = [model_or_models]
        else:
            models_list = model_or_models
        for model_item in models_list:
            queryset = model_item.objects.all()
            data.append(serializers.serialize(format, queryset))
        return data

    def add_folder(self, zip_config, path_root, path_zip):
        """
        Backup a folder into zip file
        """
        # First, some encoding sentences to avoid problems with zipfile module
        path_root = smart_str(path_root)
        path_zip = smart_str(path_zip)
        for i, (dirpath, dirnames, filenames) in enumerate(os.walk(path_root)):
            # HACK: Avoid adding files from hidden directories
            dirnames_copy = list(dirnames)
            for dirname in dirnames_copy:
                if dirname.startswith("."):
                    dirnames.remove(dirname)
            for filename in filenames:
                # Exclude compiled, hidden and temporal files
                if not (filename.endswith(".pyc") or dirname.endswith("~") or
                    filename.startswith(".")):
                    file_path = os.path.join(dirpath, filename)
                    dir_path = dirpath.replace(path_root, path_zip)
                    zip_path = os.path.join(dir_path, filename)
                    zip_config.write(file_path, zip_path)
