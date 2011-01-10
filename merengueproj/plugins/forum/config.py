from merengue.pluggable import Plugin

from plugins.forum.models import Forum, ForumCategory
from plugins.forum.admin import ForumAdmin, ForumCategoryAdmin


class PluginConfig(Plugin):
    name = 'Forum'
    description = 'Forum plugin'
    version = '0.0.1a'

    config_params = [
    ]

    url_prefixes = (
        ('forum', 'plugins.forum.urls'),
    )

    required_plugins = {'feedback': {},
                        }

    @classmethod
    def get_model_admins(cls):
        return [(Forum, ForumAdmin),
                (ForumCategory, ForumCategoryAdmin)]

    @classmethod
    def get_perms(cls):
        return (
            ('Moderate forum', 'moderate_forum', [Forum]), )
