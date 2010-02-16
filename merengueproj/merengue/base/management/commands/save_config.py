import os
import zipfile
from optparse import make_option

from django.db.models import get_models
from django.db.models.loading import load_app
from django.conf import settings
from django.core import serializers
from django.core.management.base import CommandError, LabelCommand

from merengue.base.management.base import MerengueCommand
from merengue.plugins.models import RegisteredPlugin
from merengue.plugins.utils import get_plugin_module_name


class Command(LabelCommand, MerengueCommand):

    option_list = LabelCommand.option_list + (
        make_option('-o', '--overwrite', action='store_true', dest='overwrite',
                    default=False, help="Overwrite the zip file"),
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
        zip_config = zipfile.ZipFile(path_zip, "w",
                                     compression=zipfile.ZIP_DEFLATED)
        self.add_plugins(zip_config, path_zip)
        self.add_theme(zip_config, path_zip)
        self.add_config(zip_config, path_zip)
        zip_config.close()
        print 'File created successfully in path %s' % path_zip

    def add_plugins(self, zip_config, path_zip):
        plugins = RegisteredPlugin.objects.filter(installed=True)
        for plugin in plugins:
            plugin_path = plugin.get_path()
            plugin_path_zip = os.path.join("plugins", plugin.directory_name)
            self.add_folder(zip_config, plugin_path, plugin_path_zip)
            self.add_fixtures(zip_config, plugin, plugin_path, plugin_path_zip)

    def add_theme(self, zip_config, path_zip):
        pass

    def add_config(self, zip_config, path_zip):
        pass

    def add_fixtures(self, zip_config, plugin, plugin_path, plugin_path_zip):
        plugin_modname = get_plugin_module_name(plugin.directory_name)
        plugin_mod = load_app(plugin_modname)
        plugin_models = get_models(plugin_mod)
        data = []
        format = 'json'
        for plugin_model in plugin_models:
            queryset = plugin_model.objects.all()
            data.append(serializers.serialize(format, queryset))
        fixtures_file = os.path.join(plugin_path_zip, "fixtures.%s" % format)
        zip_config.writestr(fixtures_file, "\n".join(data))

    def add_folder(self, zip_config, path_root, path_zip):
        for i, (dirpath, dirnames, filenames) in enumerate(os.walk(path_root)):
            # HACK: Avoid adding files from hidden directories
            dirnames_copy = list(dirnames)
            for dirname in dirnames_copy:
                if dirname.startswith("."):
                    dirnames.remove(dirname)
            for filename in filenames:
                if not (filename.endswith(".pyc") or dirname.endswith("~") or
                    filename.startswith(".")):
                    file_path = os.path.join(dirpath, filename)
                    dir_path = dirpath.replace(path_root, path_zip)
                    zip_path = os.path.join(dir_path, filename)
                    zip_config.write(file_path, zip_path)
