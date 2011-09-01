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

from django.core.exceptions import FieldError
from django.utils.translation import get_language_from_request
from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from searchform.forms import sanitize_filters
from searchform.utils import QueryStringManager
from merengue.base.models import BaseContent
from merengue.internallinks.forms import BaseContentSearchForm


def _filter_with_language(query, filters, lang):
    results = query
    for key, value in filters.items():
        try:
            results = results.filter(**{key: value})
        except FieldError:
            (field, operator) = key.rsplit('__', 1)
            newkey = '%s_%s__%s' % (field, lang, operator)
            results = results.filter(**{newkey: value})
    return results


def _exclude_with_language(query, excluders, lang):
    results = query
    for key, value in excluders.items():
        try:
            results = results.exclude(**{key: value})
        except FieldError:
            (field, operator) = key.rsplit('__', 1)
            newkey = '%s_%s__%s' % (field, lang, operator)
            results = results.exclude(**{newkey: value})
    return results


def internal_links_search(request):
    qsm = QueryStringManager(request, [], 'page')
    filters = sanitize_filters(qsm.get_filters())
    excluders = sanitize_filters(qsm.get_excluders())
    lang = get_language_from_request(request)
    if filters or excluders:
        results = _filter_with_language(BaseContent.objects.all(), filters, lang)
        results = _exclude_with_language(results, excluders, lang)
    else:
        results = BaseContent.objects.none()

    extra_content = dict(
        query_string=qsm.get_query_string(),
        result_msg=_(u'%s contents found') % results.count(),
        search_form=BaseContentSearchForm(_('Content'), qsm),
        title=_(u'Contents searcher'),
        )

    return list_detail.object_list(request, results,
                                   template_name='internallinks/internal_links_search.html',
                                   allow_empty=True,
                                   extra_context=extra_content,
                                   template_object_name='object')
