from merengue.pluggable import Plugin

from plugins.forum.actions import CreateThreadAction
from plugins.forum.admin import ForumAdmin, ForumCategoryAdmin, ForumSectionAdmin
from plugins.forum.models import Forum, ForumCategory


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

    def models(self):
        return [(Forum, ForumAdmin),
                (ForumCategory, ForumCategoryAdmin)]

    def section_models(self):
        return [(Forum, ForumSectionAdmin)]

    def get_actions(self):
        return [CreateThreadAction]

    def get_perms(self):
        return (
            ('Moderate forum', 'moderate_forum', [Forum]),
            ('Create new thread', 'create_new_thread', [Forum]),
        )
