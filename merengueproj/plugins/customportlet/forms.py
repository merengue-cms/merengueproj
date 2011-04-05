from django import forms

from merengue.base.forms import BaseAdminModelForm
from merengue.base.widgets import CustomTinyMCE

from cmsutils.forms.widgets import ColorPickerWidget
from plugins.customportlet.models import CustomPortlet


class CustomPortletForm(forms.ModelForm):
    class Meta:
        model = CustomPortlet

    def __init__(self, *args, **kwargs):
        super(CustomPortletForm, self).__init__(*args, **kwargs)
        descriptions_fields = ['es', 'fr', 'en']
        for prefix in descriptions_fields:
            key = 'description_%s' % prefix
            self.fields[key].widget = CustomTinyMCE(
                extra_mce_settings={'inplace_edit': True, 'height': 120, })


class CustomPortletAdminModelForm(BaseAdminModelForm):
    class Meta:
        exclude = ('order', )

    def __init__(self, *args, **kwargs):
        super(CustomPortletAdminModelForm, self).__init__(*args, **kwargs)
        self.fields['link_color'].widget = ColorPickerWidget()
