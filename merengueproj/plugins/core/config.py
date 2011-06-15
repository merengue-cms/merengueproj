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

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params
from merengue.multimedia.admin import PhotoAdmin, VideoAdmin, AudioAdmin
from merengue.multimedia.models import Photo, Video, Audio
from merengue.section.admin import DocumentRelatedModelAdmin, DocumentAdmin
from merengue.section.models import Document

from plugins.core.actions import AdminAction, LoginAction, LogoutAction, PrintAction, HotLinkAction
from plugins.core.blocks import (CoreMenuBlock, NavigationBlock,
                                 PortalMenuBlock, ContactInfoBlock,
                                 AnnouncementsBlock, PortalLinksBlock)
from plugins.core.panels import (InplaceEditPanel, InlineTransPanel, VersionPanel,
                                 InvalidateCachePanel, AddBlockPanel)


class PluginConfig(Plugin):
    name = 'Core'
    description = 'Core plugin'
    version = '0.0.1a'

    url_prefixes = (
        ('core', 'plugins.core.urls'),
    )

    config_params = [
        params.Content(name='home_initial_content',
                       label=_('home initial content'), default=1),
        params.Single(name='login_url',
                       label=_('Login URL'), default=settings.LOGIN_URL)]

    def get_actions(self):
        return [AdminAction, LoginAction, LogoutAction, PrintAction, HotLinkAction]

    def get_blocks(self):
        return [CoreMenuBlock, NavigationBlock, PortalMenuBlock,
                ContactInfoBlock, AnnouncementsBlock, PortalLinksBlock]

    def get_toolbar_panels(self):
        return [InplaceEditPanel, InlineTransPanel, AddBlockPanel,
                InvalidateCachePanel, VersionPanel, ]

    def models(self):
        return [
            (Document, DocumentAdmin),
            (Photo, PhotoAdmin),
            (Video, VideoAdmin),
            (Audio, AudioAdmin),
        ]

    def section_models(self):
        return [(Document, DocumentRelatedModelAdmin)]

    def get_perms(self):
        return ()

    def get_section_prefixes(self):
        return (reverse('section_index'), )
