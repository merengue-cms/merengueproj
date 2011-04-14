from django.contrib.admin.filterspecs import FilterSpec
from django.utils.translation import ugettext_lazy as _


class ContentBlockFilterSpec(FilterSpec):

    def __init__(self, f, request, params, model, model_admin, field_path):
        super(ContentBlockFilterSpec, self).__init__(f, request, params, model, model_admin, field_path)
        self.lookup_kwarg = 'content__isnull'
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)

    def title(self):
        return _('content block')

    def choices(self, cl):
        for k, v in ((_('All'), None), (_('Yes'), 'false'), (_('No'), 'true')):
            yield {
                'selected': self.lookup_val == v,
                'query_string': cl.get_query_string({self.lookup_kwarg: v}),
                'display': k,
                }
