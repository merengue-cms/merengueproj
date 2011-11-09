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

import zipfile
from django import forms
from django.utils.translation import ugettext_lazy as _

from merengue.base.forms import BaseForm


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
