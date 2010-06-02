from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import BaseAdmin, BaseCategoryAdmin
from plugins.standingout.forms import StandingOutAdminModelForm
from plugins.standingout.models import StandingOut, StandingOutCategory


class StandingOutAdmin(BaseAdmin):
    list_display = ('obj', 'related', 'standing_out_category')
    list_filter = ordering = ('related_content_type', 'related_id', 'obj_content_type', 'id')
    form = StandingOutAdminModelForm

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
