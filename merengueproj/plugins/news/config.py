# plugin data
NAME = 'News'
DESCRIPTION = 'News plugin'
VERSION = '0.0.1a'

# media subdir for this plugin
MEDIA_DIR = 'news'

# all plugins URLs will be below "news/" prefix
URL_PREFIX = 'news'


def activate_plugin(registry, plugin):
    """ activate plugin """
    registry.activate_plugin(plugin)
    # more stuff ...
