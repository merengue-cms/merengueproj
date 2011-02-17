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

from merengue.base.admin import PluginAdmin, RelatedModelAdmin
from merengue.base.models import BaseContent

from plugins.voting.forms import VoteForm
from plugins.voting.models import Vote


class VoteAdmin(PluginAdmin):
    form = VoteForm


class VoteRelatedModelAdmin(VoteAdmin, RelatedModelAdmin):
    related_field = 'content'
    one_to_one = True


def register(site):
    """ Merengue admin registration callback """
    site.register(Vote, VoteAdmin)
    site.register_related(Vote, VoteRelatedModelAdmin, related_to=BaseContent)
