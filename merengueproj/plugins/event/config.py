from merengue.plugin import Plugin

from plugins.event.admin import EventCategoryAdmin
from plugins.event.blocks import EventsCalendarBlock
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
        return [(Event, EventCategoryAdmin)]

    @classmethod
    def get_blocks(cls):
        return [EventsCalendarBlock]
