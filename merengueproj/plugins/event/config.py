from merengue.plugins import Plugin

from plugins.event.admin import EventSectionAdmin
from plugins.event.models import Event


class PluginConfig(Plugin):
    name = 'Events'
    description = 'Events plugin'
    version = '0.0.1a'
    url_prefixes = (
        ('event', 'plugins.event.urls'),
    )

    @classmethod
    def section_models(cls):
        return [(Event, EventSectionAdmin)]
