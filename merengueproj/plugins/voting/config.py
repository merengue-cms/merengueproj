# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

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
        params.Bool(name='readonly', label=_('is readonly?'), default=False),
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
