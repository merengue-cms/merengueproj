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

from merengue.base.forms import BaseAdminModelForm
from merengue.section.models import BaseSection
from plugins.microsite.models import MicroSite
from django.utils.translation import ugettext_lazy as _


class MicroSiteAdminForm(BaseAdminModelForm):

    def clean(self):
        # because of Django limitations, unicity constraints are only
        # checked against direct parents, so MicroSite's slug could not
        # be unique among other BaseContents'
        cleaned_data = super(MicroSiteAdminForm, self).clean()
        slug = self.cleaned_data.get('slug', None)
        if slug and self.instance.id and slug != self.instance.slug:
            if MicroSite.objects.filter(slug__exact=slug).count() or \
                    BaseSection.objects.filter(slug__exact=slug).count():
                invalid_slug = _('A MicroSite or Section with this slug already exists')
                self._errors["slug"] = self.error_class([invalid_slug])
                del cleaned_data['slug']
        return cleaned_data
