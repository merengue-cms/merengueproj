# -*- coding: utf-8 -*-
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

from merengue.block.blocks import Block, BaseBlock
from merengue.registry.items import ContentTypeFilterProvider
from plugins.addthis import params


DEFAULT_SERVICES = [
    ('facebook', u'Facebook'),
    ('twitter', u'Twitter'),
    ('email', u'Email'),
    ('print', _(u'Print')),
    ('delicious', u'Delicious'),
    ('googlebuzz', u'Google Buzz'),
    ('meneame', u'Menéame'),
    ('digg', u'Digg'),
    ]


class AddThisBlock(ContentTypeFilterProvider, Block):
    name = 'AddThisBlock'
    default_place = 'aftercontent'
    help_text = _('Block that displays AddThis links')
    verbose_name = _('AddThis service block')

    config_params = BaseBlock.config_params + ContentTypeFilterProvider.config_params + [
        params.AjaxListParam(
            name="services",
            label=_("Services do you want to show on "),
            choices=DEFAULT_SERVICES,
        ),
    ]
    default_caching_params = {
        'enabled': False,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def render(self, request, place, context,
               *args, **kwargs):
        services = self.get_config().get(
            'services', []).get_value()
        if self.match_type(context.get('content', None)):
            return self.render_block(
                request, template_name='addthis/links_block.html',
                block_title=_('Share this'),
                context={'services': services},
                )
        else:
            return ''
