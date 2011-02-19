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
from plugins.feedback.blocks import FeedbackBlock


class PluginConfig(Plugin):
    name = 'Feedback'
    description = 'Feedback plugin'
    version = '0.0.1'
    url_prefixes = (
        ('feedback', 'plugins.feedback.urls'),
    )

    config_params = [
        params.Integer(name='number_of_comments', label=_('Number of comment for each content'), default=-1),
        params.Bool(name='show_children', label=_('Show children'), default=True),
        params.Bool(name='show_links', label=_('Show options bar'), default=True),
    ]

    def get_blocks(self):
        return [FeedbackBlock]
