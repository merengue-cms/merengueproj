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
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import BaseOrderableAdmin, BaseCategoryAdmin, OrderableRelatedModelAdmin, RelatedModelAdmin
from merengue.base.models import BaseContent
from plugins.standingout.forms import StandingOutAdminModelForm
from plugins.standingout.models import StandingOut, StandingOutCategory


class StandingOutAdmin(BaseOrderableAdmin):
    list_display = ('obj', 'related', 'standing_out_category')
    list_filter = ('related_content_type', 'related_id', 'obj_content_type', 'id')
    form = StandingOutAdminModelForm
    sortablefield = 'order'

    def get_form(self, request, obj=None):
        self.fieldsets = None
        form = super(StandingOutAdmin, self).get_form(request, obj)
        self.fieldsets = (
                (_('Basic Options'), {
                                'fields': ('obj', )}),
                (_('Advanced Options'), {
                                'fields': ('standing_out_category', 'related')}),
        )
        return form


class StandingSectionOutAdmin(StandingOutAdmin, OrderableRelatedModelAdmin):

    list_display = ('obj', )
    standingoutcategory = 'section'

    def get_form(self, request, obj=None):
        form_class = super(StandingSectionOutAdmin, self).get_form(request, obj)
        self.fieldsets = (self.fieldsets[0], )
        return form_class

    def get_ordering(self):
        return ('order', 'asc')

    def save_model(self, request, obj, form, change):
        standingoutcategory = StandingOutCategory.objects.get(context_variable=self.standingoutcategory)
        obj.standing_out_category = standingoutcategory
        obj.related = self.basecontent
        super(RelatedModelAdmin, self).save_model(request, obj, form, change)

    def queryset(self, request, basecontent=None):
        base_qs = super(RelatedModelAdmin, self).queryset(request)
        if basecontent is None:
            # we override our related content
            basecontent = self.basecontent
        ct = ContentType.objects.get_for_model(basecontent)
        return base_qs.filter(**{'related_id': basecontent.id,
                                 'related_content_type': ct})


class StandingContentOutAdmin(StandingSectionOutAdmin):

    standingoutcategory = 'content'


class StandingOutCategoryAdmin(BaseCategoryAdmin):
    list_display = BaseCategoryAdmin.list_display + ('context_variable', )


def register(site):
    """ Merengue admin registration callback """
    site.register(StandingOut, StandingOutAdmin)
    site.register(StandingOutCategory, StandingOutCategoryAdmin)
    site.register_related(StandingOut, StandingContentOutAdmin,
                          related_to=BaseContent)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(StandingOut)
    site.unregister(StandingOutCategory)
