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
    from plugins.filebrowser.config import PluginConfig
    return os.path.join(settings.MEDIA_ROOT, PluginConfig.get_config()['filebrowser_root'].get_value())


def get_location():
    from plugins.filebrowser.config import PluginConfig
    return os.path.join(settings.MEDIA_ROOT, PluginConfig.get_config()['filebrowser_docs_root'].get_value())


def get_base_url():
    from plugins.filebrowser.config import PluginConfig
    return os.path.join(settings.MEDIA_URL, PluginConfig.get_config()['filebrowser_docs_url'].get_value())
