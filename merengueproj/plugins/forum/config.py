from merengue.pluggable import Plugin

from plugins.forum.models import Forum
from plugins.forum.admin import ForumAdmin


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
        return [(Forum, ForumAdmin)]
