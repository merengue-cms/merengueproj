from django.forms.util import ErrorList

from merengue.base.forms import BaseAdminModelForm


class StandingOutAdminModelForm(BaseAdminModelForm):

    def clean(self):
        cleaned_data = super(StandingOutAdminModelForm, self).clean()
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
