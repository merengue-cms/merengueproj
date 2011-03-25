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

import datetime

from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from merengue.base.forms import BaseAdminModelForm


class EventAdminForm(BaseAdminModelForm):

    def clean(self):
        cleaned_data = super(EventAdminForm, self).clean()
        end = cleaned_data.get('end', None)
        start = cleaned_data.get('start', None)
        if end and start:
            if (end - start) <= datetime.timedelta(0):
                end_error = self._errors.get('end', ErrorList([]))
                end_error_new = ErrorList([_(u'The end date has to be after the start date')])
                end_error.extend(end_error_new)
                self._errors['end'] = ErrorList(end_error)
        return cleaned_data
