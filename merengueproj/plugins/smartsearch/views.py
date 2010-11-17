from django.http import HttpResponseRedirect

from autoreports.models import modelform_factory

from plugins.smartsearch.models import Searcher
from plugins.smartsearch.forms import SearcherForm


def search_is_valid(request, searcher_id):
    searcher = Searcher.objects.get(pk=searcher_id)
    form_search_class = modelform_factory(model=searcher.content_type.model_class(),
                                          form=SearcherForm)
    data = request.GET
    form_search = form_search_class(data=data, fields=searcher.report_filter_fields_tuple, is_admin=False, report=searcher)
    __full_path = "%s?%s" %(data.get('__path'), request.GET.urlencode())
    if not form_search.is_valid():
        __full_path = "%s&__ignore_filters=1" %__full_path
    return HttpResponseRedirect(__full_path)
