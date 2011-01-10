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

from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import BaseOrderableAdmin, BaseCategoryAdmin
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


class StandingOutCategoryAdmin(BaseCategoryAdmin):
    list_display = BaseCategoryAdmin.list_display + ('context_variable', )


def register(site):
    """ Merengue admin registration callback """
    site.register(StandingOut, StandingOutAdmin)
    site.register(StandingOutCategory, StandingOutCategoryAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(StandingOut)
    site.unregister(StandingOutCategory)
