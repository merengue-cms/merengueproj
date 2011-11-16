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
import sorl

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import BaseOrderableAdmin, BaseCategoryAdmin, OrderableRelatedModelAdmin, RelatedModelAdmin
from merengue.base.models import BaseContent
from merengue.section.models import BaseSection
from plugins.standingout.forms import StandingOutAdminModelForm
from plugins.standingout.models import StandingOut, StandingOutCategory

from transmeta import get_real_fieldname_in_each_language


class StandingOutAdmin(BaseOrderableAdmin):
    list_display = ('__unicode__', 'related', 'standing_out_category', 'order')
    list_filter = ('related_content_type', 'related_id', 'obj_content_type', 'id')
    form = StandingOutAdminModelForm
    sortablefield = 'order'
    sortablereverse = True
    html_fields = ('short_description', )
    exclude = ('order', )

    def get_form(self, request, obj=None):
        self.fieldsets = None
        form = super(StandingOutAdmin, self).get_form(request, obj)
        self.fieldsets = (
                (_('Basic Options'), {
                                'fields': get_real_fieldname_in_each_language('title') +\
                                          get_real_fieldname_in_each_language('short_description') +\
                                          ['url', 'obj', 'image']}),
                (_('Advanced Options'), {
                                'fields': ('standing_out_category', 'related')}),
        )
        return form

    def save_model(self, request, obj, form, change):
        saved = super(StandingOutAdmin, self).save_model(request, obj, form, change)
        # if we changed the image, its thumbnail is no longer valid.
        if obj.id and 'image' in form.changed_data:
            sorl.thumbnail.delete(obj.image, delete_file=False)
        return saved


class StandingContentOutAdmin(OrderableRelatedModelAdmin, StandingOutAdmin):

    list_display = ('__unicode__', 'order')
    sortablefield = 'order'
    sortablereverse = True

    def get_form(self, request, obj=None):
        form_class = super(StandingContentOutAdmin, self).get_form(request, obj)
        self.fieldsets = (self.fieldsets[0], )
        return form_class

    def get_ordering(self):
        return ('order', 'desc')

    def changelist_view(self, request, extra_context=None, parent_model_admin=None, parent_object=None):
        extra_context = self._update_extra_context(request, extra_context, parent_model_admin, parent_object)
        return super(StandingOutAdmin, self).changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        if self.basecontent and isinstance(self.basecontent, BaseSection):
            category = 'section'
        else:
            category = 'content'
        standingoutcategory = StandingOutCategory.objects.get(context_variable=category)
        obj.standing_out_category = standingoutcategory
        obj.related = self.basecontent
        setattr(obj, self.sortablefield, self.queryset(request).count())
        super(RelatedModelAdmin, self).save_model(request, obj, form, change)

    def queryset(self, request, basecontent=None):
        base_qs = super(RelatedModelAdmin, self).queryset(request)
        if basecontent is None:
            # we override our related content
            basecontent = self.basecontent
        ct = ContentType.objects.get_for_model(basecontent)
        return base_qs.filter(**{'related_id': basecontent.id,
                                 'related_content_type': ct})


class StandingOutCategoryAdmin(BaseCategoryAdmin):
    list_display = BaseCategoryAdmin.list_display + ('context_variable', )


def register(site):
    """ Merengue admin registration callback """
    site.register_related(StandingOut, StandingContentOutAdmin,
                          related_to=BaseContent)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister_related(StandingOut, StandingContentOutAdmin,
                            related_to=BaseContent)
