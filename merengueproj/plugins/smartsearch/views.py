from django.http import HttpResponseRedirect

from autoreports.model_forms import modelform_factory

from plugins.smartsearch.models import Searcher
from plugins.smartsearch.forms import SearcherForm
from plugins.smartsearch.utils import get_fields


def search_is_valid(request, searcher_id):
    search = Searcher.objects.get(pk=searcher_id)
    model = search.content_type.model_class()
    form_search_class = modelform_factory(model=model,
                                          form=SearcherForm)
    data = request.GET
    form_search_class.base_fields = get_fields(search)
    form_search = form_search_class(data=data, is_admin=False, search=search)

    __full_path = "%s?" % data.get('__path')
    del data['__path']
    __full_path = "%s%s" % (__full_path, request.GET.urlencode())

    if not form_search.is_valid():
        __full_path = "%s&__ignore_filters=1" % __full_path
    return HttpResponseRedirect(__full_path)
