from django import forms

from merengue.section.models import DocumentSection
from cmsutils.forms import widgets


class DocumentSectionForm(forms.ModelForm):

    class Meta:
        model = DocumentSection

    def __init__(self, *args, **kwargs):
        super(DocumentSectionForm, self).__init__(*args, **kwargs)
        self.fields['body_es'].widget = widgets.TinyMCE(extra_mce_settings={'inplace_edit': True, 'height': 120, })
