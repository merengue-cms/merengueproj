from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params

from plugins.voting.admin import VoteAdmin
from plugins.voting.models import Vote
from plugins.voting.blocks import VotingBlock
from plugins.voting.viewlets import BaseContentWithMoreVotes, BaseContentTopRated


class PluginConfig(Plugin):
    name = 'Voting'
    description = 'Voting plugin'
    version = '0.0.1a'
    url_prefixes = (
        ('voting', 'plugins.voting.urls'),
    )

    config_params = [
        params.Single(name='readonly', label=_('is readonly?'), default=False),
    ]

    @classmethod
    def get_blocks(cls):
        return [VotingBlock]

    @classmethod
    def get_model_admins(cls):
        return [(Vote, VoteAdmin)]

    @classmethod
    def get_viewlets(cls):
        return [BaseContentWithMoreVotes, BaseContentTopRated]
