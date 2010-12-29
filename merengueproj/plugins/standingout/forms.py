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
        if cleaned_data.get('standing_out_category', None) and not cleaned_data.get('related', None):
            related_error = self._errors.get('related', ErrorList([]))
            related_error_new = ErrorList([_(u'If you select the option in field standing out category you have to select a option in related field')])
            related_error.extend(related_error_new)
            self._errors['related'] = ErrorList(related_error)
        elif not cleaned_data.get('standing_out_category', None) and cleaned_data.get('related', None):
            standing_out_category_error = self._errors.get('standing_out_category', ErrorList([]))
            standing_out_category_error_new = ErrorList([_(u'If you select the option in field related you have to select a option in standing out category field')])
            standing_out_category_error.extend(standing_out_category_error_new)
            self._errors['standing_out_category'] = ErrorList(standing_out_category_error)
        if not self._errors:
            for unique in self._meta.model._meta.unique_together:
                dict_filter = {}
                for field in unique:
                    dict_filter[field] = cleaned_data.get(field, None)
                try:
                    obj = self._meta.model.objects.get(**dict_filter)
                    obj_error = self._errors.get('obj', ErrorList([]))
                    obj_error_new = ErrorList([_(u'There was a object with the same fields pk=%s') % obj.id])
                    obj_error.extend(obj_error_new)
                    self._errors['obj'] = ErrorList(obj_error)
                except self._meta.model.DoesNotExist:
                    pass
        return cleaned_data
