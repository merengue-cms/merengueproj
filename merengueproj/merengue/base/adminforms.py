import zipfile
from django import forms
from django.utils.translation import ugettext_lazy as _
from merengue.base.forms import BaseForm


class UploadConfigForm(BaseForm):
    zipfile = forms.FileField(label=_("Select a .zip file:"))

    def clean_zipfile(self):
        data = self.cleaned_data['zipfile']
        try:
            zip_config = zipfile.ZipFile(data, "r",
                                         compression=zipfile.ZIP_DEFLATED)
            return zip_config
        except zipfile.BadZipfile, zipfile.LargeZipfile:
            raise forms.ValidationError(_("Bad or too large .zip file"))
