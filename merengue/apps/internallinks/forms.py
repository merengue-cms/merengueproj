from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from searchform.forms import SearchForm
from searchform.terms import TextSearchTerm


class BaseContentSearchForm(SearchForm):

    fields = SortedDict((
        ('name', TextSearchTerm(_(u'The name'), _(u'Name'), _(u'which name'))),
        ('plain_description_es', TextSearchTerm(_(u'The description'), _(u'Description'), _(u'which description'))),
        ))
