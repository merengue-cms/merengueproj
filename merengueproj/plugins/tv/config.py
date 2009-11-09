from merengue.plugins import Plugin


class PluginConfig(Plugin):
    name = 'Tv'
    description = 'Tv plugin'
    version = '0.0.1a'

    url_prefixes = (
        ('canales-de-television', 'plugins.tv.urls'),
    )
