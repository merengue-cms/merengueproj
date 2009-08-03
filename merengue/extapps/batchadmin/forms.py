from django import forms
from django.conf import settings

from django.utils.translation import ugettext_lazy as _

CHECKBOX_NAME = 'selected'

def get_media_prefix():
    default = "batchadmin/"
    return getattr(settings, 'BATCHADMIN_MEDIA_PREFIX', default)

def get_jquery_js():
    default = get_media_prefix() + "js/jquery.js"
    return getattr(settings, 'BATCHADMIN_JQUERY_JS', default)

class ActionForm(forms.Form):
    class Media:
        css = {'all': (get_media_prefix() + "css/batchadmin.css",)}
        js = (get_jquery_js(), get_media_prefix() + "js/batchadmin.js",)

    action = forms.ChoiceField(label=_('Action'))

checkbox = forms.CheckboxInput({'class': 'batch-select'}, lambda value: False)