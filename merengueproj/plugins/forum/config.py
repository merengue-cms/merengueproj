from merengue.pluggable import Plugin

from plugins.forum.models import Forum, ForumCategory
from plugins.forum.admin import ForumAdmin, ForumCategoryAdmin, ForumSectionAdmin


class PluginConfig(Plugin):
    name = 'Forum'
    description = 'Forum plugin'
    version = '0.0.1a'

    config_params = [
    ]

    url_prefixes = (
        ({'en': 'forum',
          'es': 'foros'},
         'plugins.forum.urls'),
    )

    required_plugins = {'feedback': {},
                        }

    def section_models(self):
        return [(Forum, ForumSectionAdmin)]

    def get_model_admins(self):
        return [(Forum, ForumAdmin),
                (ForumCategory, ForumCategoryAdmin)]

    def get_perms(self):
        return (
            ('Moderate forum', 'moderate_forum', [Forum]), )
