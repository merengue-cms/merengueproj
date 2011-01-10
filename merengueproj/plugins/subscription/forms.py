from django import forms
from django.utils.translation import ugettext_lazy as _
from plugins.subscription.models import Subscribable


class SubscribableAdminForm(forms.ModelForm):
    model = Subscribable

    def clean(self):
        cleaned_data = self.cleaned_data
        start_date = cleaned_data['start_date']
        end_date = cleaned_data['end_date']
        if end_date < start_date:
            raise forms.ValidationError(_('End date should be greater than start date.'))
        return super(SubscribableAdminForm, self).clean()
