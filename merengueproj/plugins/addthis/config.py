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

from merengue.pluggable import Plugin
## from merengue.registry import params

from plugins.addthis.blocks import AddThisBlock
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


class PluginConfig(Plugin):
    name = 'AddThis service'
    description = 'Plugin that includes a new block with AddThis service'
    version = '0.0.1a'

    config_params = [
        params.AjaxListParam(
            name="services",
            label=_("Services do you want to show on "),
            choices=DEFAULT_SERVICES,
        ),
    ]

    @classmethod
    def get_blocks(cls):
        return [AddThisBlock, ]
