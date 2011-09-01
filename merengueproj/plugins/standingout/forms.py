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

from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from merengue.base.forms import BaseAdminModelForm


class StandingOutAdminModelForm(BaseAdminModelForm):

    def clean(self):
        cleaned_data = super(StandingOutAdminModelForm, self).clean()
        category = cleaned_data.get('standing_out_category', None)
        related = cleaned_data.get('related', None)
        if not category and related:
            standing_out_category_error = self._errors.get('standing_out_category', ErrorList([]))
            standing_out_category_error_new = ErrorList([_(u'If you select the option in field related you have to select a option in standing out category field')])
            standing_out_category_error.extend(standing_out_category_error_new)
            self._errors['standing_out_category'] = ErrorList(standing_out_category_error)
        return cleaned_data
