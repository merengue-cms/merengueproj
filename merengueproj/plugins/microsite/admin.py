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

from merengue.section.admin import SectionAdmin
from plugins.microsite.models import MicroSite
from plugins.microsite.forms import MicroSiteAdminForm
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple


class MicroSiteAdmin(SectionAdmin):
    form = MicroSiteAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(MicroSiteAdmin, self).get_form(request, obj, **kwargs)
        choices = getattr(settings, 'MICROSITE_AVAILABLE_EXCLUDE_PLACES', [])
        if not choices:
            del(form.base_fields['exclude_places'])
        else:
            form.base_fields['exclude_places'].widget = FilteredSelectMultiple(
                '', False,
                choices=[(i, i) for i in choices])
        return form


def register(site):
    """ Merengue admin registration callback """
    site.register(MicroSite, MicroSiteAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(MicroSite)
