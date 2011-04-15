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
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from autoreports.forms import FormAdminDjango, ReportFilterForm
from autoreports.wizards import ReportNameForm


class SearcherRelatedCollectionModelAdminForm(ReportNameForm, FormAdminDjango):

    name = forms.CharField(label=_('name'), required=False)

    def __init__(self, *args, **kwargs):
        super(SearcherRelatedCollectionModelAdminForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.is_required = False

    def __unicode__(self):
        return self.as_django_admin()

    class Meta:
        exclude = ('content_type', 'options',)


class SearcherForm(ReportFilterForm):

    def __init__(self, is_admin=False, use_subfix=True, search=None, *args, **kwargs):
        self.search = search
        super(SearcherForm, self).__init__(is_admin, use_subfix, *args, **kwargs)

    class Media:
        js = (reverse("django.views.i18n.javascript_catalog"),
              settings.ADMIN_MEDIA_PREFIX + "js/core.js",
             )
        css = {'all': (settings.ADMIN_MEDIA_PREFIX + 'css/forms.css',
                      )}
