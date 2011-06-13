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

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _, ugettext_lazy

from merengue.registry import params
from merengue.block.blocks import Block, BaseBlock
from plugins.standingout.models import StandingOut, StandingOutCategory
from transmeta import get_fallback_fieldname


class StandingOutBlock(Block):
    name = 'standingout'
    default_place = 'rightsidebar'
    help_text = ugettext_lazy('Block with standing out by categories')
    verbose_name = ugettext_lazy('Standing out block')

    config_params = BaseBlock.config_params + [
        params.Integer(name='limit', label=_('limit for standingouts in block'), default='5'),
    ]

    default_caching_params = {
        'enabled': True,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def render(self, request, place, context, block_content_relation=None,
               *args, **kwargs):
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
        limit = self.get_config().get('limit', None)
        if limit:
            standingouts = standingouts[:limit.get_value()]
        return self.render_block(request, template_name='block_standingout.html',
                                 block_title=_('Search'),
                                 context={'standingouts': standingouts})


class StandingOutSlideShowBlock(Block):
    name = 'standingout-slideshow'
    default_place = 'homepage'
    help_text = ugettext_lazy('Block with a jquery slideshow of standingouts')
    verbose_name = ugettext_lazy('Standing out Slide Show block')

    config_params = BaseBlock.config_params + [
        params.Integer(name='limit', label=_('limit for standingouts in block'), default='5'),
    ]
    default_caching_params = {
        'enabled': True,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def render(self, request, place, context, block_content_relation=None,
               *args, **kwargs):
        (category, created) = StandingOutCategory.objects.get_or_create(slug='slideshow')
        name_field = get_fallback_fieldname('name')
        if (created):
            setattr(category, name_field, 'slideshow')
            category.save()
        standingouts = StandingOut.objects.filter(standing_out_category=category)
        limit = self.get_config().get('limit', None)
        if limit:
            standingouts = standingouts[:limit.get_value()]
        return self.render_block(request, template_name='block_slideshow.html',
                                 block_title=_('Slideshow'),
                                 context={'standingouts': standingouts})
