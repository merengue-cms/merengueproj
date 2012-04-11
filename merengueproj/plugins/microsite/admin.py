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
from plugins.microsite.models import MicroSite, MicroSiteLink
from plugins.microsite.forms import MicroSiteAdminForm
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from merengue.base.admin import SimpleOrderableRelatedModelAdmin, BaseAdmin
from transmeta import get_fallback_fieldname
from django.utils.translation import ugettext_lazy as _


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
            if obj:
                if isinstance(obj.exclude_places, list):
                    initial = obj.exclude_places
                else:
                    initial = obj.exclude_places and obj.exclude_places.split('\n')
                    obj.exclude_places = initial
                form.base_fields['exclude_places'].initial = initial
        return form


class MicroSiteLinkAdmin(SimpleOrderableRelatedModelAdmin):

    list_display = BaseAdmin.list_display
    list_filter = ('visible_by_roles', )
    related_field = 'microsite'
    sortablefield = 'order'
    tool_label = _('highlight menu')
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}


def register(site):
    """ Merengue admin registration callback """
    site.register(MicroSite, MicroSiteAdmin)
    site.register_related(MicroSiteLink, MicroSiteLinkAdmin, related_to=MicroSite)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(MicroSite)
    site.unregister_related(MicroSiteLink, MicroSiteLinkAdmin, related_to=MicroSite)
