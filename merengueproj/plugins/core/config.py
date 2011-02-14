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
from merengue.section.admin import DocumentRelatedModelAdmin
from merengue.section.models import Document

from plugins.core.actions import AdminAction, LoginAction, LogoutAction, PrintAction
from plugins.core.blocks import (CoreMenuBlock, NavigationBlock,
                                 PrimaryLinksBlock, SecondaryLinksBlock,
                                 PortalMenuBlock, ContactInfoBlock)
from plugins.core.panels import InplaceEditPanel, InlineTransPanel, VersionPanel


class PluginConfig(Plugin):
    name = 'Core'
    description = 'Core plugin'
    version = '0.0.1a'

    url_prefixes = (
    )

    config_params = [
        params.Content(name='home_initial_content',
                       label=_('home initial content'), default=1)]

    @classmethod
    def get_actions(cls):
        return [AdminAction, LoginAction, LogoutAction, PrintAction]

    @classmethod
    def get_blocks(cls):
        return [CoreMenuBlock, NavigationBlock, PrimaryLinksBlock,
                SecondaryLinksBlock, PortalMenuBlock, ContactInfoBlock]

    @classmethod
    def get_toolbar_panels(cls):
        return [InplaceEditPanel, InlineTransPanel, VersionPanel]

    @classmethod
    def section_models(cls):
        # section_models of merengue core
        return [(Document, DocumentRelatedModelAdmin)]

    @classmethod
    def get_perms(cls):
        return ()
        # an example was:
        #return (
        #    ('vote', _('Vote content')),
        #    ('mark_as_finished', _('View any content'), models=[Document]),
        #)
