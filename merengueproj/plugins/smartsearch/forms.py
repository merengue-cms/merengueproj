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
from django.conf import settings
from django.core.urlresolvers import reverse

from autoreports.forms import FormAdminDjango, ReportFilterForm
from merengue.base.forms import BaseAdminModelForm


class SearcherRelatedCollectionModelAdminForm(BaseAdminModelForm, FormAdminDjango):

    def __unicode__(self):
        return self.as_django_admin()

    class Meta:
        exclude = ('content_type', 'report_filter_fields',
                   'report_display_fields', 'advanced_options')


class SearcherForm(ReportFilterForm):

    class Media:
        js = (reverse("django.views.i18n.javascript_catalog"),
              settings.ADMIN_MEDIA_PREFIX + "js/core.js",
             )
        css = {'all': (settings.ADMIN_MEDIA_PREFIX + 'css/forms.css',
                      )}
