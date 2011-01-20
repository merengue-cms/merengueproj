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

from merengue.base.admin import BaseAdmin, RelatedModelAdmin
from merengue.base.forms import BaseAdminModelForm

from merengue.section.models import Section

from plugins.contentmenu.models import ContentGroup


class ContentGroupAdmin(BaseAdmin):
    form = BaseAdminModelForm
    filter_horizontal = ('contents', )


class ContentGroupSectionAdmin(ContentGroupAdmin, RelatedModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        class_form = super(ContentGroupSectionAdmin, self).get_form(request, obj=None, **kwargs)
        base_qs = class_form.base_fields['contents'].queryset
        class_form.base_fields['contents'].queryset = base_qs.filter(basesection=self.basecontent)
        return class_form

    def queryset(self, request, basecontent=None):
        base_qs = super(RelatedModelAdmin, self).queryset(request)
        if basecontent is None:
            # we override our related content
            basecontent = self.basecontent
        return base_qs.filter(contents__basesection=basecontent)


def register(site):
    """ Merengue admin registration callback """
    site.register(ContentGroup, ContentGroupAdmin)
    site.register_related(ContentGroup, ContentGroupSectionAdmin,
                          related_to=Section)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(ContentGroup)
