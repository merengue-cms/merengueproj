from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from searchform.forms import SearchForm
from searchform.terms import TextSearchTerm, ObjectsSearchTerm
from places.terms import ContentClassSearchTerm
from places.models import Province, BaseCity


class BaseContentSearchForm(SearchForm):

    class ProvinceSearchTerm(ObjectsSearchTerm):
        model = Province

    class CitySearchTerm(ObjectsSearchTerm):
        model = BaseCity

    class BaseContentClassSearchTerm(ContentClassSearchTerm):
        hide = []

    fields = SortedDict((
        ('name', TextSearchTerm(_(u'The name'), _(u'Name'), _(u'which name'))),
        ('plain_description_es', TextSearchTerm(_(u'The description'), _(u'Description'), _(u'which description'))),
        ('location__cities', CitySearchTerm(_(u'The city'), _(u'City'), _(u'which city'))),
        ('location__cities__province', ProvinceSearchTerm(_(u'The province'), _(u'Province'), _(u'which province'))),
        ('class_name', BaseContentClassSearchTerm(_(u'Type'), _(u'Type'), _(u'which type'))),
        ))
