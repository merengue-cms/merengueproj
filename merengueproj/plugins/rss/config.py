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

from merengue.base.models import BaseContent
from merengue.pluggable import Plugin
from merengue.registry import params

from plugins.rss.actions import GenerateRSS
from plugins.rss.blocks import RSSGlobalFeed


def get_children_classes(content_type):
    subclasses = content_type.__subclasses__()
    result = []
    for subclass in subclasses:
        result += get_children_classes(subclass)
        result += [subclass]
    return result


def get_all_children_classes(content_type=BaseContent):
    return [(x.__name__, x.__name__) for x in get_children_classes(content_type)]


class PluginConfig(Plugin):
    name = 'RSS syndication'
    description = 'Plugin to allow RSS syndication of contents'
    version = '0.0.1a'

    url_prefixes = (
        ('rss', 'plugins.rss.urls'),
    )

    config_params = [
        params.List(
            name="contenttypes",
            label=_("Content types that whant to be syndicated"),
            choices=get_all_children_classes,
        ),
        params.PositiveInteger(
            name="limit",
            label=_("number of elements to show at the feed"),
            default=10,
        ),
        params.Single(
            name="portal",
            label=_("portal name that will be shown as RSS title"),
            default="Merengue RSS"
        ),
    ]

    @classmethod
    def get_actions(cls):
        return [GenerateRSS]

    @classmethod
    def get_model_admins(cls):
        return []

    @classmethod
    def get_blocks(cls):
        return [RSSGlobalFeed, ]
