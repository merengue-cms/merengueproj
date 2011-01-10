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

from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from transmeta import get_fallback_fieldname

from searchform.forms import SearchForm
from searchform.terms import TextSearchTerm


class BaseContentSearchForm(SearchForm):

    fields = SortedDict((
        ('name', TextSearchTerm(_(u'The name'), _(u'Name'), _(u'which name'))),
        (get_fallback_fieldname('plain_description'), TextSearchTerm(_(u'The description'), _(u'Description'), _(u'which description'))),
        ))
