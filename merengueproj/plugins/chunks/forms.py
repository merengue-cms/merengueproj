# -*- encoding: utf-8 -*-
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

from merengue.base.forms import BaseAdminModelForm

replace_dict = {u'á': u'&aacute;', u'é': u'&eacute;', u'í': u'&iacute;',
                u'ó': u'&oacute;', u'ú': u'&uacute;', u'ñ': '&ntilde;',
                u'Ñ': '&Ntilde;'}


class ChunkAdminModelForm(BaseAdminModelForm):

    def clean(self):
        if self.cleaned_data.get('content'):
            for key in self.cleaned_data['content'].keys():
                self.cleaned_data['content'][key] = ''.join(map(replace, self.cleaned_data['content'][key]))
        return self.cleaned_data


def replace(c):
    if c in replace_dict.keys():
        return replace_dict[c]
    else:
        return c
