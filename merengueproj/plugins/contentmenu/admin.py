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

from ajax_select.fields import AutoCompleteSelectField

from django.contrib import admin
from django.utils.translation import ugettext

from merengue.base.admin import BaseAdmin, RelatedModelAdmin
from merengue.base.forms import BaseAdminModelForm

from merengue.section.models import BaseSection

from plugins.contentmenu.models import ContentGroup, ContentGroupContent


class BaseContentInline(admin.TabularInline):
    model = ContentGroupContent
    extra = 1
    template = 'contentmenu/admin/tabular.html'

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'basecontent':
            return AutoCompleteSelectField('section_contentlink',
                label=ugettext('content'),
                help_text=ugettext('content selected here will be shown when entering the section'))
        return super(BaseContentInline, self).formfield_for_dbfield(db_field, **kwargs)


class ContentGroupAdmin(BaseAdmin):
    form = BaseAdminModelForm
    filter_horizontal = ('contents', )
    inlines = [BaseContentInline, ]

    def _media(self):
        __media = super(ContentGroupAdmin, self)._media()
        __media.add_js(['contentmenu/js/menu-sort-tabular.js'])
        return __media
    media = property(_media)


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
