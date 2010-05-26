from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import BaseAdmin, BaseCategoryAdmin
from plugins.standingout.models import StandingOut, StandingOutCategory


class StandingOutAdmin(BaseAdmin):
    list_display = ('obj', 'related', 'standing_out_category')
    list_filter = ordering = ('related_content_type', 'related_id', 'obj_content_type', 'id')

    def get_form(self, request, obj=None):
        self.fieldsets = None
        form = super(StandingOutAdmin, self).get_form(request, obj)

        def clean(self):
            cleaned_data = super(self.__class__, self).clean()
            cleaned_data.update(self.clean_old())
            if cleaned_data.get('standing_out_category', None) and not cleaned_data.get('related', None):
                related_error = self._errors.get('related', ErrorList([]))
                related_error_new = ErrorList([u'If you select the option in field standing out category you have to select a option in related field'])
                related_error.extend(related_error_new)
                self._errors['related'] = ErrorList(related_error)
            elif not cleaned_data.get('standing_out_category', None) and cleaned_data.get('related', None):
                standing_out_category_error = self._errors.get('standing_out_category', ErrorList([]))
                standing_out_category_error_new = ErrorList([u'If you select the option in field related you have to select a option in standing out category field'])
                standing_out_category_error.extend(standing_out_category_error_new)
                self._errors['standing_out_category'] = ErrorList(standing_out_category_error)
            return cleaned_data

        form.clean_old = form.clean
        form.clean = clean
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
