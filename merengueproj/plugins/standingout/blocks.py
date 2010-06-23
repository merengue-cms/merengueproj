# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from merengue.block.blocks import Block
from plugins.standingout.models import StandingOut, StandingOutCategory


class StandingOutBlock(Block):
    name = 'standingout'
    default_place = 'rigthsidebar'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        standingout_categories = StandingOutCategory.objects.all()
        standingouts = None
        for standingout_category in standingout_categories:
            varible_value = context.get(standingout_category.context_variable, None)
            if varible_value:
                contenttype = ContentType.objects.get_for_model(varible_value)
                standingouts = StandingOut.objects.filter(related_id=varible_value.pk, related_content_type=contenttype)
                if standingouts:
                    break
        standingouts = standingouts or StandingOut.objects.filter(related_content_type__isnull=True, related_id__isnull=True)
        return cls.render_block(request, template_name='standingout/block_standingout.html',
                                block_title=_('Search'),
                                context={'standingouts': standingouts})
