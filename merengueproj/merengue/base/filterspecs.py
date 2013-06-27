from django.contrib.admin.filterspecs import AllValuesFilterSpec, RelatedFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

from merengue.workflow import utils as workflow_api


class ClassnameFilterSpec(AllValuesFilterSpec):

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
               'query_string': cl.get_query_string({}, [self.field.name]),
               'display': _('All')}
        for val in self.lookup_choices:
            val = smart_unicode(val)
            yield {'selected': self.lookup_val == val,
                   'query_string': cl.get_query_string({self.field.name: val}),
                   'display': _(val)}


class WorkflowStatusSpec(RelatedFilterSpec):
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        super(WorkflowStatusSpec, self).__init__(
              f, request, params, model, model_admin, field_path=field_path)

        queryset = workflow_api.workflow_by_model(model).states.all()
        self.lookup_choices = [(x._get_pk_val(), smart_unicode(x)) for x in queryset]
