from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from merengue.base.models import BaseContent
from cmsutils.adminfilters import QueryStringManager
from internallinks.forms import BaseContentSearchForm


def internal_links_search(request):
    qsm = QueryStringManager(request, [], 'page')
    filters = qsm.get_filters()
    excluders = qsm.get_excluders()
    if filters or excluders:
        results = BaseContent.objects.filter(**filters)
        results = results.exclude(**excluders)
    else:
        results = BaseContent.objects.none()

    extra_content = dict(
        query_string=qsm.get_query_string(),
        result_msg=_(u'%s contents found') % results.count(),
        search_form = BaseContentSearchForm('sdf', qsm, template='base/searchform.html'),
        title=_(u'Contents searcher'),
        )

    return list_detail.object_list(request, results,
                                   template_name = 'internallinks/internal_links_search.html',
                                   allow_empty=True,
                                   extra_context=extra_content,
                                   template_object_name='object')
