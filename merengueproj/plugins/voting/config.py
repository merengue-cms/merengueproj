from merengue.plugin import Plugin
from plugins.voting.blocks import VotingBlock


class PluginConfig(Plugin):
    name = 'Voting'
    description = 'Voting plugin'
    version = '0.0.1a'
    url_prefixes = (
        #('voting', 'plugins.voting.urls'),
    )

    @classmethod
    def get_blocks(cls):
        return [VotingBlock]
