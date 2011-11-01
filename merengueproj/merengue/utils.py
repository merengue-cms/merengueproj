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

import csv
import ConfigParser
import os
import zipfile
from datetime import datetime
from cStringIO import StringIO

from django.conf import settings
from django.core import serializers
from django.core.management.color import no_style
from django.core.management.base import CommandError
from django.db import connection, transaction
from django.db.models import get_models
from django.db.models.loading import load_app
from django.utils.encoding import smart_str


class classproperty(property):
    """ decorator to allow define python property on class methods """

    def __get__(self, obj, type_):
        return self.fget.__get__(None, type_)()

    def __set__(self, obj, value):
        cls = type(obj)
        return self.fset.__get__(None, cls)(value)


def copy_request(request, delete_list, copy=None):
    from copy import deepcopy
    request_copy = copy and copy(request) or deepcopy(request)
    for delete_item in delete_list:
        if delete_item in request_copy.GET:
            del request_copy.GET[delete_item]
    return request_copy


def save_config(overwrite=True, save_all=True):
    from merengue.registry import RegisteredItem
    from merengue.action.models import RegisteredAction
    from merengue.pluggable.models import RegisteredPlugin
    from merengue.block.models import RegisteredBlock
    from merengue.theming.models import Theme
    buffer = StringIO()
    zip_config = zipfile.ZipFile(buffer, "w",
                                     compression=zipfile.ZIP_DEFLATED)
    models_to_save = (
        (RegisteredItem, "registry"),
        (RegisteredAction, "actions"),
        (RegisteredBlock, "blocks"),
        (RegisteredPlugin, "plugins"),
        (Theme, "themes"),
    )
    add_models(zip_config, models_to_save)
    add_plugins(zip_config, save_all=save_all)
    add_config(zip_config, save_all=save_all)
    if save_all:
        add_theme(zip_config)
    zip_config.close()
    return buffer


def save_backupdb(path_backup):
    buffer = StringIO()
    zip_config = zipfile.ZipFile(buffer, "w",
                                     compression=zipfile.ZIP_DEFLATED)
    f = file(path_backup)
    zip_config.writestr(path_backup.split('/')[-1], f.read())
    zip_config.close()
    return buffer


def add_models(zip_config, models_to_save):
    """
    Add models in tuple of tuples models_to_save
    (ModelClass, "file_name")
    """
    for model_to_save in models_to_save:
        model = model_to_save[0]
        file_name = model_to_save[1]
        fixtures = get_fixtures(model)
        format = 'xml'
        fixtures_file = "%s.%s" % (file_name, format)
        zip_config.writestr(fixtures_file, "\n".join(fixtures))


def add_theme(zip_config):
    """
    Add all data themes related. The save_config argument sets if
    all data is saved or only fixtures.
    """
    from merengue.theming.models import Theme
    themes = Theme.objects.filter(active=True)
    for theme in themes:
        theme_path = theme.get_path()
        theme_path_zip = os.path.join("themes", theme.directory_name)
        add_folder(zip_config, theme_path, theme_path_zip)


def add_plugins(zip_config, save_all=False):
    """
    Add all data plugins related. The save_config argument sets if
    all data is saved or only fixtures.
    """
    from merengue.pluggable.models import RegisteredPlugin
    plugins = RegisteredPlugin.objects.filter(installed=True)
    for plugin in plugins:
        plugin_path = plugin.get_path()
        plugin_path_zip = os.path.join("plugins", plugin.directory_name)
        if save_all:
            add_folder(zip_config, plugin_path, plugin_path_zip)
        add_fixtures(zip_config, plugin, plugin_path, plugin_path_zip)


def add_config(zip_config, save_all=False):
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
    config_string = StringIO()
    config.write(config_string)
    zip_config.writestr('config.ini', config_string.getvalue())
    config_string.close()


def add_fixtures(zip_config, plugin, plugin_path, plugin_path_zip):
    """
    Backup fixtures into zip file
    """
    from merengue.pluggable.utils import get_plugin_module_name
    # next two sentences is for avoiding problems with zipfile module
    # (encoding errors)
    plugin_path = smart_str(plugin_path)
    plugin_path_zip = smart_str(plugin_path_zip)
    plugin_modname = get_plugin_module_name(plugin.directory_name)
    plugin_mod = load_app(plugin_modname)
    plugin_models = get_models(plugin_mod)
    fixtures = get_fixtures(plugin_models)
    format = 'xml'
    fixtures_file = os.path.join(plugin_path_zip, "fixtures.%s" % format)
    zip_config.writestr(fixtures_file, "\n".join(fixtures))


def get_fixtures(model_or_models, format='xml'):
    data = []
    format = format.lower()
    if not isinstance(model_or_models, (list, tuple)):
        models_list = [model_or_models]
    else:
        models_list = model_or_models
    for model_item in models_list:
        queryset = model_item.objects.all()
        serialized_string = serializers.serialize(format, queryset)
        data.append(serialized_string)
    return data


def add_folder(zip_config, path_root, path_zip):
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
            if not (filename.endswith(".pyc") or filename.endswith("~") or
                filename.startswith(".")):
                file_path = os.path.join(dirpath, filename)
                dir_path = dirpath.replace(path_root, path_zip)
                zip_path = os.path.join(dir_path, filename)
                zip_config.write(file_path, zip_path)


def restore_config(zip_config):
    from merengue.action.models import RegisteredAction
    from merengue.block.models import RegisteredBlock
    from merengue.registry import RegisteredItem
    from merengue.pluggable.models import RegisteredPlugin
    from merengue.pluggable.utils import install_plugin
    from merengue.theming.models import Theme
    config = get_config(zip_config)
    restore_all = (config.get("mode", "fixtures") == "all")
    version = config.get("version", "MERENGUE_VERSION")
    # TODO: Implement method to get current merengue version
    if "MERENGUE_VERSION" != version:
        raise CommandError("Merengue version error")  # To fix. CommandError can not be displayed TTW.
    models_to_restore = (
        (RegisteredItem, "registry"),  # this has to be first in tuple
        (RegisteredAction, "actions"),
        (RegisteredBlock, "blocks"),
        (RegisteredPlugin, "plugins"),
        (Theme, "themes"),
    )
    restore_models(zip_config, models_to_restore)
    if restore_all:
        # TODO: Implement "all" mode restore
        pass
    for plugin in RegisteredPlugin.objects.filter(installed=True):
        install_plugin(plugin)
    zip_config.close()
    print 'File restored successfully'


def get_config(zip_config):
    """
    Extract and return a dictionary with configuration parameters
    from zipped config.ini file
    """
    config_fp = StringIO(zip_config.read("config.ini"))
    config = ConfigParser.ConfigParser()
    config.readfp(config_fp, 'r')
    config_dic = {}
    config_items = config.items("main")
    # From list of tuples to dict
    [config_dic.update({item[0]: item[1]}) for item in config_items]
    return config_dic


def restore_models(zip_config, models_to_restore):
    """
    Add models in tuple of tuples models_to_restore to merengue database
    (ModelClass, "file_name")
    """
    sid = transaction.savepoint()
    try:
        models = set()
        for model_to_restore, file_name in models_to_restore:
            model_to_restore.objects.all().delete()  # we first delete all objects to avoid duplication problems
            format = 'xml'
            fixtures_file_name = "%s.%s" % (file_name, format)
            fixtures_data = zip_config.read(fixtures_file_name)
            fixtures = serializers.deserialize(format, fixtures_data)
            has_objects = False
            for fixture in fixtures:
                if fixture:
                    has_objects = True
                    fixture.save()
                models.add(fixture.object.__class__)
        # HACK: If we found even one object in a fixture, we need to reset
        # the database sequences.
        if has_objects:
            sequence_reset_sql(models)
    except:
        transaction.savepoint_rollback(sid)
        raise
    else:
        transaction.savepoint_commit(sid)


def sequence_reset_sql(models):
    """
    Reset the database sequences
    """
    cursor = connection.cursor()
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
    if sequence_sql:
        for line in sequence_sql:
            cursor.execute(line)


def bin_exists(binary):
    """ function to find a binary in the system """
    bin_search_path = [path for path in os.environ['PATH'].split(os.pathsep)
                       if os.path.isdir(path)]
    mode = os.R_OK | os.X_OK
    for path in bin_search_path:
        pathbin = os.path.join(path, binary)
        if os.access(pathbin, mode) == 1:
            return True
    return False


def get_all_parents(model, parents=None):
    parents = parents or ()
    parents_level_1 = model.__bases__
    for pl1 in parents_level_1:
        parents += get_all_parents(pl1, parents)
        parents += parents_level_1
    return parents


def is_last_application(app):
    """ returns Merengue last application """
    last_app = settings.MERENGUE_APPS[-1].split('.')[1]
    return app == last_app


def ask_yesno_question(question, default_answer):
    while True:
        prompt = '%s: (yes/no) [%s]: ' % (question, default_answer)
        answer = raw_input(prompt).strip()
        if answer == '':
            return default_answer == 'yes' and True or False
        elif answer in ('yes', 'no'):
            return answer == 'yes' and True or False
        else:
            print 'Please answer yes or no'


def print_sql_queries(base_path):
    now = datetime.now()
    file_name = 'sqls_%s%s.csv' % (now.strftime('%Y%m%d%H%M%S'), str(now.microsecond))
    fout = open(os.path.join(base_path, file_name), 'w')
    csv_stream = csv.writer(fout, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for query in connection.queries:
        csv_stream.writerow([query['sql'], query['time']])
    fout.close()
