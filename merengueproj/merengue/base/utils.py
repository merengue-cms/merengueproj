from django.conf import settings
from django.core.cache import cache
from django.utils.cache import _generate_cache_header_key
from django.utils.encoding import smart_str

from cStringIO import StringIO
import ConfigParser
import os
import zipfile

from merengue.action.models import RegisteredAction
from merengue.block.models import RegisteredBlock
from merengue.plugin.models import RegisteredPlugin
from merengue.plugin.utils import get_plugin_module_name
from merengue.registry import RegisteredItem
from merengue.theme.models import Theme

from django.db.models import get_models
from django.db.models.loading import load_app
from django.core import serializers


if settings.USE_GIS:
    from geopy import geocoders
    from merengue.base.models import Location

    def geolocate_object_base(object_base_content):
        if not object_base_content.location:
            object_base_content.location=Location.objects.create()
        city = object_base_content.location.cities.all()
        city = (city and city[0]) or ""
        address = object_base_content.location.address or ""
        number = object_base_content.location.number or ""
        postal_code = object_base_content.location.postal_code or ""
        address_type = ""
        if object_base_content.location.address_type_id and object_base_content.location.address_type.name != 'Otros':
            address_type = object_base_content.location.address_type.name or ""

        query = u"%s %s %s %s %s, andalusia, spain" % (address_type, address, number, postal_code, city)
        query = smart_str(query.strip())
        g = geocoders.Google(settings.GOOGLE_MAPS_API_KEY, 'maps.google.es')
        try:
            place_google, (lat, lon) = g.geocode(query)
            object_base_content.location.main_location = 'POINT(%f %f)' % (lon, lat)
            object_base_content.location.save()
            object_base_content.is_autolocated = True
            object_base_content.save()
        except ValueError, e:
            pass


def copy_request(request, delete_list):
    from copy import deepcopy
    request_copy = deepcopy(request)
    for delete_item in delete_list:
        if delete_item in request_copy.GET:
            del request_copy.GET[delete_item]
    return request_copy


def invalidate_cache_for_path(request_path):
    """ invalidates cache based on request.path """
    # wrap a dummy request object for call django function

    class Request(object):
        pass

    request = Request()
    request.path = request_path
    cache_header_key = _generate_cache_header_key(settings.CACHE_MIDDLEWARE_KEY_PREFIX, request)
    cache.delete(cache_header_key)


def save_config(overwrite=True, save_all=True):
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


def add_models(zip_config, models_to_save):
    """
    Add models in tuple of tuples models_to_save
    (ModelClass, "file_name")
    """
    for model_to_save in models_to_save:
        model = model_to_save[0]
        file_name = model_to_save[1]
        fixtures = get_fixtures(model)
        format = 'json'
        fixtures_file = "%s.%s" % (file_name, format)
        zip_config.writestr(fixtures_file, "\n".join(fixtures))


def add_theme(zip_config):
    """
    Add all data themes related. The save_config argument sets if
    all data is saved or only fixtures.
    """
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
    # next two sentences is for avoiding problems with zipfile module
    # (encoding errors)
    plugin_path = smart_str(plugin_path)
    plugin_path_zip = smart_str(plugin_path_zip)
    plugin_modname = get_plugin_module_name(plugin.directory_name)
    plugin_mod = load_app(plugin_modname)
    plugin_models = get_models(plugin_mod)
    fixtures = get_fixtures(plugin_models)
    format = 'json'
    fixtures_file = os.path.join(plugin_path_zip, "fixtures.%s" % format)
    zip_config.writestr(fixtures_file, "\n".join(fixtures))


def get_fixtures(model_or_models, format='json'):
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
            if not (filename.endswith(".pyc") or dirname.endswith("~") or
                filename.startswith(".")):
                file_path = os.path.join(dirpath, filename)
                dir_path = dirpath.replace(path_root, path_zip)
                zip_path = os.path.join(dir_path, filename)
                zip_config.write(file_path, zip_path)
