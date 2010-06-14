from django.core.exceptions import FieldError
from django.utils.translation import get_language_from_request
from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from cmsutils.adminfilters import QueryStringManager
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
    filters = qsm.get_filters()
    excluders = qsm.get_excluders()
    lang = get_language_from_request(request)
    if filters or excluders:
        results = _filter_with_language(BaseContent.objects.all(), filters, lang)
        results = _exclude_with_language(results, excluders, lang)
    else:
        results = BaseContent.objects.none()

    extra_content = dict(
        query_string=qsm.get_query_string(),
        result_msg=_(u'%s contents found') % results.count(),
        search_form = BaseContentSearchForm(_('Content'), qsm),
        title=_(u'Contents searcher'),
        )

    return list_detail.object_list(request, results,
                                   template_name = 'internallinks/internal_links_search.html',
                                   allow_empty=True,
                                   extra_context=extra_content,
                                   template_object_name='object')
