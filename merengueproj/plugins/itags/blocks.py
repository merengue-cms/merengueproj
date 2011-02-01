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

from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.block.blocks import Block
from merengue.registry import params
from merengue.registry.items import BlockQuerySetItemProvider
from plugins.itags.viewlets import TagCloudViewlet


class TagCloudBlock(BlockQuerySetItemProvider, Block):
    name = 'tagcloud'
    verbose_name = _('Tag cloud')
    help_text = _('Block with a tag cloud')
    default_place = 'leftsidebar'

    config_params = BlockQuerySetItemProvider.config_params + [
        params.PositiveInteger(
            name='max_tags_in_cloud',
            label=_('Max number of tags in cloud'),
            default=20,
        ),
    ]

    @classmethod
    def render(cls, request, place, context, block_content_relation=None,
               *args, **kwargs):
        if block_content_relation:
            custom_config = block_content_relation.get_block_config_field()
        else:
            custom_config = None
        config = cls.get_merged_config(custom_config)
        limit = config.get('max_tags_in_cloud', []).get_value()
        filter_section = config.get('filtering_section', False).get_value()
        tag_cloud = TagCloudViewlet.get_tag_cloud(request, context, limit, filter_section)
        return cls.render_block(request, template_name='itags/blocks/tagcloud.html',
                                block_title=ugettext('Tag cloud'),
                                context={'taglist': tag_cloud,
                                         'filter_section': filter_section},
                                block_content_relation=block_content_relation)
