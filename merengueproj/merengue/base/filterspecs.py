from django.contrib.admin.filterspecs import AllValuesFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _


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
