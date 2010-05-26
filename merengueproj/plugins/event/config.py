from merengue.pluggable import Plugin

from plugins.event.admin import EventAdmin, EventCategoryAdmin, EventSectionAdmin
from plugins.event.blocks import EventsCalendarBlock
from plugins.event.models import Event, Category


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

    @classmethod
    def get_blocks(cls):
        return [EventsCalendarBlock]

    @classmethod
    def get_model_admins(cls):
        return [(Event, EventAdmin),
                (Category, EventCategoryAdmin)]
