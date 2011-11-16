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

from ajax_select.fields import AutoCompleteSelectMultipleField

from django.utils.translation import ugettext

from merengue.base.admin import BaseAdmin, RelatedModelAdmin
from merengue.base.forms import BaseAdminModelForm

from merengue.section.models import BaseSection

from plugins.contentmenu.models import ContentGroup


class ContentGroupAdmin(BaseAdmin):
    form = BaseAdminModelForm
    filter_horizontal = ('contents', )

    def get_form(self, request, obj=None, **kwargs):
        form = super(ContentGroupAdmin, self).get_form(request, obj, **kwargs)
        if 'contents' in form.base_fields.keys():
            field = form.base_fields['contents']
            link_autocomplete = AutoCompleteSelectMultipleField(
                'section_contentlink', label=field.label,
            )
            link_autocomplete.widget.help_text = ugettext('content selected here will be shown when entering the section')
            form.base_fields['contents'] = link_autocomplete
        return form


class ContentGroupSectionAdmin(RelatedModelAdmin, ContentGroupAdmin):

    def _base_update_extra_context(self, extra_context=None):
        extra_context = super(ContentGroupSectionAdmin, self)._base_update_extra_context(extra_context)
        extra_context.update({'parent_object': self.basecontent})
        return extra_context

    def save_model(self, request, obj, form, change):
        super(RelatedModelAdmin, self).save_model(request, obj, form, change)

    def queryset(self, request, basecontent=None):
        base_qs = super(RelatedModelAdmin, self).queryset(request).filter(contents__sections=self.basecontent).distinct()
        return base_qs


def register(site):
    """ Merengue admin registration callback """
    site.register(ContentGroup, ContentGroupAdmin)
    site.register_related(ContentGroup, ContentGroupSectionAdmin,
                          related_to=BaseSection)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(ContentGroup)
    site.unregister_related(ContentGroup, ContentGroupSectionAdmin,
                          related_to=BaseSection)
