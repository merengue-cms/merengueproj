# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from autoreports.forms import FormAdminDjango
from merengue.base.forms import BaseAdminModelForm


class SearcherRelatedCollectionModelAdminForm(BaseAdminModelForm, FormAdminDjango):

    def __unicode__(self):
        return self.as_django_admin()

    class Meta:
        exclude = ('content_type', 'report_filter_fields',
                   'report_display_fields', 'advanced_options')
