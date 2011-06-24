# Copyright (c) 2010 by Yaco Sistemas <precio@yaco.es>
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

from pprint import pprint  # pyflakes:ignore
from django.test import TestCase

from merengue.base.models import BaseContent
from merengue.block.blocks import Block, ContentBlock, SectionBlock
from merengue.block.utils import get_all_blocks_to_display
from merengue.registry import register
from merengue.section.models import BaseSection


class BaseBlock(Block):

    def render(self, request, place, context, *args, **kwargs):
        reg_block = self.reg_item
        # the rendering should be an string, but we return a dict for testing purposes
        return {
            'name': self.name,
            'place': reg_block.placed_at,
            'content': reg_block.content_id,
            'order': reg_block.order,
            'overwrite_if_place': reg_block.overwrite_if_place,
            'overwrite_always': reg_block.overwrite_always,
        }


class LeftBlock(BaseBlock):
    name = 'leftblock'
    default_place = 'leftsidebar'


class RightBlock(BaseBlock):
    name = 'rightblock'
    default_place = 'rightsidebar'


class FooterBlock(BaseBlock):
    name = 'footerblock'
    default_place = 'footer'


class FooContentBlock(BaseBlock, ContentBlock):
    name = 'foocontentblock'
    default_place = 'leftsidebar'


class FooSectionBlock(BaseBlock, SectionBlock):
    name = 'foosectionblock'
    default_place = 'leftsidebar'


class ContentRelatedBlock(BaseBlock):
    name = 'contentrelatedblock'
    default_place = 'leftsidebar'


def get_block_names(place=None, content=None, section=None):
    return [b['name'] for b in get_rendered_blocks(place, content, section)]


def get_rendered_blocks(place=None, content=None, section=None):
    blocks = get_all_blocks_to_display(place, content, section)
    return [reg_block.get_registry_item().render(None, None, None) for reg_block in blocks]


class BlockTestCase(TestCase):

    def setUp(self):
        self.maxDiff = None  # to get large diff when a test fail
        reg_block = register(LeftBlock)
        reg_block.order = 0
        reg_block.save()
        reg_block = register(RightBlock)
        reg_block.order = 1
        reg_block.save()
        reg_block = register(FooterBlock)
        reg_block.order = 2
        reg_block.save()
        reg_block = register(FooContentBlock)
        reg_block.order = 3
        reg_block.save()
        reg_block = register(FooSectionBlock)
        reg_block.order = 4
        reg_block.save()
        self.content = BaseContent.objects.create(name_en='A content')
        content_reg_block = register(ContentRelatedBlock)
        content_reg_block.order = 5
        content_reg_block.content = self.content
        content_reg_block.save()
        self.content_2 = BaseContent.objects.create(name_en='Other content')
        content_reg_block_2 = register(ContentRelatedBlock)
        content_reg_block_2.order = 6
        content_reg_block_2.content = self.content_2
        content_reg_block_2.save()
        self.section = BaseSection.objects.create(name_en='A section')
        disabled_block = register(LeftBlock)
        disabled_block.active = False  # this block should not be visible
        disabled_block.save()

    def test_rendering_places(self):
        """Test the blocks retrieved in every place are the block Merengue should display """
        left_blocks_rendered = [
            {'name': 'leftblock', 'place': u'leftsidebar', 'content': None, 'order': 0, 'overwrite_if_place': True, 'overwrite_always': False},
            {'name': 'foocontentblock', 'place': u'leftsidebar', 'content': None, 'order': 3, 'overwrite_if_place': True, 'overwrite_always': False},
            {'name': 'foosectionblock', 'place': u'leftsidebar', 'content': None, 'order': 4, 'overwrite_if_place': True, 'overwrite_always': False},
        ]
        right_blocks_rendered = [
            {'name': 'rightblock', 'place': u'rightsidebar', 'content': None, 'order': 1, 'overwrite_if_place': True, 'overwrite_always': False},
        ]
        footer_blocks_rendered = [
            {'name': 'footerblock', 'place': u'footer', 'content': None, 'order': 2, 'overwrite_if_place': True, 'overwrite_always': False},
        ]
        left_blocks_rendered_in_content = [
            {'content': None, 'name': 'leftblock', 'order': 0, 'overwrite_always': False, 'overwrite_if_place': True, 'place': u'leftsidebar'},
            {'content': None, 'name': 'foocontentblock', 'order': 3, 'overwrite_always': False, 'overwrite_if_place': True, 'place': u'leftsidebar'},
            {'content': None, 'name': 'foosectionblock', 'order': 4, 'overwrite_always': False, 'overwrite_if_place': True, 'place': u'leftsidebar'},
            {'name': 'contentrelatedblock', 'place': u'leftsidebar', 'content': self.content.id, 'order': 5, 'overwrite_if_place': True, 'overwrite_always': False},
        ]
        right_blocks_rendered_in_content = [
            {'name': 'rightblock', 'place': u'rightsidebar', 'content': None, 'order': 1, 'overwrite_if_place': True, 'overwrite_always': False},
        ]
        self.assertEqual(left_blocks_rendered, get_rendered_blocks('leftsidebar'))
        self.assertEqual(right_blocks_rendered, get_rendered_blocks('rightsidebar'))
        self.assertEqual(footer_blocks_rendered, get_rendered_blocks('footer'))
        self.assertEqual(left_blocks_rendered_in_content, get_rendered_blocks('leftsidebar', self.content))
        self.assertEqual(right_blocks_rendered_in_content, get_rendered_blocks('rightsidebar', self.content))
        self.assertEqual([], get_rendered_blocks('aftercontent', self.content))

    def test_block_overwriting(self):
        """ Test block overriding behavior """
        content_reg_block = register(LeftBlock)
        content_reg_block.content = self.content
        content_reg_block.overwrite_always = True
        content_reg_block.placed_at = 'rightsidebar'
        content_reg_block.save()
        # this block will be placed in the "rightsidebar" and will hide the leftsidebar blocks
        self.assertTrue('leftblock' not in get_block_names('leftsidebar', self.content))
        # section should not affect to this
        self.assertTrue('leftblock' not in get_block_names('leftsidebar', self.content, self.section))
        # the overriding should not affect to content_2
        self.assertTrue('leftblock' in get_block_names('leftsidebar', self.content_2))
        content_reg_block.overwrite_always = False
        content_reg_block.save()
        # this block will be placed in the "rightsidebar" but wont hide the leftsidebar blocks
        self.assertTrue('leftblock' in get_block_names('leftsidebar', self.content))
        content_reg_block.overwrite_always = False
        content_reg_block.placed_at = 'leftsidebar'
        content_reg_block.save()
        # this block will be placed in the "rightsidebar" but wont hide the leftsidebar blocks
        self.assertEqual(get_block_names('leftsidebar', self.content).count('leftblock'), 1)
        content_reg_block.overwrite_if_place = False
        content_reg_block.save()
        # now the block "leftblock" should appears twice
        self.assertEqual(get_block_names('leftsidebar', self.content).count('leftblock'), 2)
