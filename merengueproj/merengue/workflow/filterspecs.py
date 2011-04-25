from django.contrib.admin.filterspecs import FilterSpec
from django.utils.translation import ugettext_lazy as _


class WorkflowModelRelatedFilterSpec(FilterSpec):

    def __init__(self, f, request, params, model, model_admin, field_path):
        super(WorkflowModelRelatedFilterSpec, self).__init__(f, request, params, model, model_admin, field_path)
        self.workflow = model_admin.basecontent
        self.lookup_kwarg = 'workflowmodelrelation__workflow'
        self.lookup_kwarg2 = 'id__isnull'
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        if self.lookup_val == None:
            self.lookup_val = request.GET.get(self.lookup_kwarg2, None)

    def title(self):
        return _('related to this workflow')

    def choices(self, cl):
        for k, v in ((_('All'), None), (_('Yes'), str(self.workflow.pk))):
            yield {
                'selected': self.lookup_val == v,
                'query_string': cl.get_query_string({self.lookup_kwarg: v, self.lookup_kwarg2: None}),
                'display': k,
                }
        k, v = (_('No'), 'false')
        yield {
            'selected': self.lookup_val == v,
            'query_string': cl.get_query_string({self.lookup_kwarg2: v, self.lookup_kwarg: None}),
            'display': k,
            }
