from merengue.plugins import Plugin


class PluginConfig(Plugin):
    name = 'Events'
    description = 'Events plugin'
    version = '0.0.1a'
    url_prefixes = (
        ('event', 'plugins.event.urls'),
    )
