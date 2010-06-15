import zipfile
from django import forms
from django.utils.translation import ugettext_lazy as _

from merengue.base.forms import BaseForm

from cmsutils.db_utils import set_backup


class BaseConfigForm(BaseForm):
    zipfile = forms.FileField(label=_("Select a .zip file:"))

    def clean_zipfile(self):
        data = self.cleaned_data['zipfile']
        try:
            zip_config = zipfile.ZipFile(data, "r",
                                         compression=zipfile.ZIP_DEFLATED)
            return zip_config
        except zipfile.BadZipfile, zipfile.LargeZipfile:
            raise forms.ValidationError(_("Bad or too large .zip file"))


class UploadConfigForm(BaseConfigForm):
    pass


class BackupForm(BaseConfigForm):

    def save(self):
        zip_config = self.cleaned_data['zipfile']
        f = zip_config.infolist()[0]
        value = zip_config.read(f.filename)
        set_backup(value)
