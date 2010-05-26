from merengue.pluggable import Plugin
from plugins.feedback.blocks import FeedbackBlock


class PluginConfig(Plugin):
    name = 'Feedback'
    description = 'Feedback plugin'
    version = '0.0.1'
    url_prefixes = (
        ('feedback', 'plugins.feedback.urls'),
    )

    @classmethod
    def get_blocks(cls):
        return [FeedbackBlock]
