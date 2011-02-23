import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class FileBrowserStorage(FileSystemStorage):
    """
    Standard filesystem storage
    """

    @property
    def location(self):
        return os.path.abspath(self.location_func())

    @property
    def base_url(self):
        return self.base_url_func()

    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.location_func = location
        self.base_url_func = base_url


def get_root_location():
    from merengue.pluggable.utils import get_plugin
    plugin_config = get_plugin('filebrowser').get_config()
    return os.path.join(settings.MEDIA_ROOT, plugin_config['filebrowser_root'].get_value())


def get_location():
    from merengue.pluggable.utils import get_plugin
    plugin_config = get_plugin('filebrowser').get_config()
    return os.path.join(settings.MEDIA_ROOT, plugin_config['filebrowser_docs_root'].get_value())


def get_base_url():
    from merengue.pluggable.utils import get_plugin
    plugin_config = get_plugin('filebrowser').get_config()
    return os.path.join(settings.MEDIA_URL, plugin_config['filebrowser_docs_url'].get_value())
