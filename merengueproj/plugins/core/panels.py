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

from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

import merengue
from merengue.uitools import panels


class InplaceEditPanel(panels.Panel):

    def render(self, context):
        self.get_config()
        return render_to_string('core/panels/inplaceedit.html', context)


class InlineTransPanel(panels.Panel):

    def render(self, context):
        return render_to_string('core/panels/inlinetrans.html', context)


class VersionPanel(panels.Panel):

    def render(self, context):
        return _('Version: %s') % merengue.get_version()
