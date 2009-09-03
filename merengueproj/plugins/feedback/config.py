from merengue.plug import Plugin
from plugins.feedback.blocks import FeedbackBlock
from django.conf import settings


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

    @classmethod
    def post_actions(cls):
        comment_app = getattr(settings, 'COMMENTS_APP', None)
        if not comment_app:
            setattr(settings, 'COMMENT_APPS', 'plugins.feedback')
