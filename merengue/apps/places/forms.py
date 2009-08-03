from django import forms
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from base.models import BaseContent
from base.forms import QuickSearchForm, AdvancedSearchForm
from places.models import BaseCity
from places.terms import (ProvinceQuickSearchTerm, TouristZoneQuickSearchTerm, CityQuickSearchTerm,
                          ProvinceSearchTerm, TouristZoneSearchTerm, CitySearchTerm,
                          ContentClassSearchTerm, CertificateResourceSearchTerm)
from searchform.registry import search_form_registry
from searchform.terms import (FreeTextSearchTerm, LongTextSearchTerm,
                              TextSearchTerm)


class BasePlacesSearchForm(object):
    results_model = BaseCity
    results_template = 'places/places_search_results.html'

    def get_selected_menu(self):
        return 'places-searcher'

    def get_selected_related_fields(self):
        return []


class PlacesQuickSearchForm(BasePlacesSearchForm, QuickSearchForm):
    title = _('Places')
    extra_scripts = ('%sjs/searchlets.js' % settings.MEDIA_URL, )
    template = 'places/quick_search_form.html'

    fields = SortedDict((
            ('name',
             FreeTextSearchTerm(_(u'City'),
                                _(u'City'),
                                _(u'which city zone'))),

            ('province',
             ProvinceQuickSearchTerm(_(u'Province'),
                                     _(u'Province'),
                                     _(u'which province'))),

            ('touristzone',
             TouristZoneQuickSearchTerm(_(u'Tourist zone'),
                                        _(u'Tourist zone'),
                                        _(u'which tourist zone'))),

            ))


class PlacesAdvancedSearchForm(BasePlacesSearchForm, AdvancedSearchForm):
    title = _('Places')

    fields = SortedDict((
            ('name',
             TextSearchTerm(_(u'Name'),
                            _(u'Name'),
                            _(u'which name'))),

            ('province',
             ProvinceSearchTerm(_(u'The province'),
                                _(u'Province'),
                                _(u'which province'))),

            ('touristzone',
             TouristZoneSearchTerm(_(u'The tourist zone'),
                                   _(u'Tourist zone'),
                                   _(u'which tourist zone'))),

            ))


class BaseProvinceResourcesSearchForm(object):
    results_model = BaseContent
    base_results_template = 'places/places_search_base.html'

    def bind_to_province(self, province):
        field = self.fields['location__cities']
        field.filters['province'] = province
        field = self.fields['location__cities__touristzone']
        field.filters['province'] = province

        self.title = '%s %s' % (ugettext('Province of'), province)

        self.binded_obj = province

    def get_results_queryset(self, request):
        return self.results_model.objects.published().filter(location__cities__province=self.binded_obj)

    def get_selected_menu(self):
        return 'province-%s' % self.binded_obj.slug


class ProvinceResourcesQuickSearchForm(BaseProvinceResourcesSearchForm, QuickSearchForm):
    extra_scripts = ('%sjs/searchlets.js' % settings.MEDIA_URL, )
    template = 'places/province_quick_search_form.html'
    title = _('Places')

    fields = SortedDict((
            ('name',
             FreeTextSearchTerm(_(u'Name'),
                                _(u'Name'),
                                _(u'which name'))),

            ('location__cities__name',
             FreeTextSearchTerm(_(u'City'),
                                _(u'City'),
                                _(u'which city zone'))),

            ('location__cities',
             CityQuickSearchTerm(_(u'City'),
                                 _(u'City'),
                                 _(u'which city'))),

            ('location__cities__touristzone',
             TouristZoneQuickSearchTerm(_(u'Tourist zone'),
                                        _(u'Tourist zone'),
                                        _(u'which tourist zone'))),


            ('class_name',
             ContentClassSearchTerm(_(u'Type'),
                                    _(u'Type'),
                                    _(u'which type'))),
            ))

    def __init__(self, *args, **kwargs):
        super(ProvinceResourcesQuickSearchForm, self).__init__(*args, **kwargs)
        self.binded_obj = None


class ProvinceResourcesAdvancedSearchForm(BaseProvinceResourcesSearchForm, AdvancedSearchForm):
    title = _('Places')

    fields = SortedDict((
            ('name',
             TextSearchTerm(_(u'Name'),
                            _(u'Name'),
                            _(u'which name'))),

            ('location__cities',
             CitySearchTerm(_(u'The city'),
                            _(u'City'),
                            _(u'which city'))),

            ('location__cities__touristzone',
             TouristZoneSearchTerm(_(u'The tourist zone'),
                                   _(u'Tourist zone'),
                                   _(u'which tourist zone'))),

            ('class_name',
             ContentClassSearchTerm(_(u'The type'),
                                    _(u'Type'),
                                    _(u'which type'))),

            ('certificates',
                CertificateResourceSearchTerm(_(u'Quality mark'),
                                              _(u'Quality mark'),
                                              _(u'which quality mark'))),

            ('plain_description_es',
             LongTextSearchTerm(_(u'Description'),
                                _(u'Description'),
                                _(u'which description'))),

            ))

    def __init__(self, *args, **kwargs):
        super(ProvinceResourcesAdvancedSearchForm, self).__init__(*args, **kwargs)
        self.binded_obj = None

    def bind_to_province(self, province):
        super(ProvinceResourcesAdvancedSearchForm, self).bind_to_province(province)
        self.title = unicode(province)


class BaseTouristZoneResourcesSearchForm(object):
    results_model = BaseContent
    base_results_template = 'places/places_search_base.html'

    def bind_to_touristzone(self, touristzone):
        self.binded_obj = touristzone

        field = self.fields['location__cities']
        field.filters['touristzone'] = touristzone

        self.title = unicode(touristzone)

    def get_results_queryset(self, request):
        return self.results_model.objects.published().filter(location__cities__touristzone=self.binded_obj)

    def get_selected_menu(self):
        return "province-%s touristzone-%s" % (self.binded_obj.province.slug,
                                               self.binded_obj.slug)


class TouristZoneResourcesQuickSearchForm(BaseTouristZoneResourcesSearchForm, QuickSearchForm):
    extra_scripts = ('%sjs/searchlets.js' % settings.MEDIA_URL, )
    template = 'places/touristzone_quick_search_form.html'
    title = _('Places')

    fields = SortedDict((
            ('name',
             FreeTextSearchTerm(_(u'Name'),
                                _(u'Name'),
                                _(u'which name'))),

            ('location__cities__name',
             FreeTextSearchTerm(_(u'City'),
                                _(u'City'),
                                _(u'which city zone'))),

            ('location__cities',
             CityQuickSearchTerm(_(u'City'),
                                 _(u'City'),
                                 _(u'which city'))),


            ('class_name',
             ContentClassSearchTerm(_(u'Type'),
                                    _(u'Type'),
                                    _(u'which type'))),
            ))

    def __init__(self, *args, **kwargs):
        super(TouristZoneResourcesQuickSearchForm, self).__init__(*args,
                                                                   **kwargs)
        self.binded_obj = None


class TouristZoneResourcesAdvancedSearchForm(BaseTouristZoneResourcesSearchForm, AdvancedSearchForm):
    title = _('Places')

    fields = SortedDict((
            ('name',
             TextSearchTerm(_(u'Name'),
                            _(u'Name'),
                            _(u'which name'))),

            ('location__cities',
             CitySearchTerm(_(u'The city'),
                            _(u'City'),
                            _(u'which city'))),

            ('class_name',
             ContentClassSearchTerm(_(u'The type'),
                                    _(u'Type'),
                                    _(u'which type'))),

            ('certificates',
                CertificateResourceSearchTerm(_(u'Quality mark'),
                                              _(u'Quality mark'),
                                              _(u'which quality mark'))),

            ('plain_description_es',
             LongTextSearchTerm(_(u'Description'),
                                _(u'Description'),
                                _(u'which description'))),

            ))

    def __init__(self, *args, **kwargs):
        super(TouristZoneResourcesAdvancedSearchForm, self).__init__(*args,
                                                                      **kwargs)
        self.binded_obj = None


class SearchFilter(forms.Form):

    def __init__(self, show_city_field=False, filters={}, *args, **kwargs):
        super(SearchFilter, self).__init__(*args, **kwargs)
        self.fields['name__icontains'] = forms.CharField(max_length=30,
                               widget=forms.TextInput(),
                               label=_(u'Name'),
                               required=False)
        if show_city_field:
            self.fields['location__cities__name__icontains'] = \
                    forms.CharField(
                                   max_length=30,
                                   widget=forms.TextInput(),
                                   label=_(u'City'),
                                   required=False)

        self._recommended_other_words = []
        self.filters = filters or {}

    def recommended_other_words(self, contents, recursive=False):
        from base.search_word import LevenshteinDistance, JaroWinkler
        if not contents:
            if settings.SEARCH_ALGORITHM == 'JAROWINKLER':
                searcher_words = JaroWinkler(**settings.PROPERTIES_JAROWINKLER)
            else:
                searcher_words = LevenshteinDistance(
                                            **settings.PROPERTIES_LEVENTEIN)
            word = self.cleaned_data.get('name__icontains')
            word_cities = self.cleaned_data.get(
                                        'location__cities__name__icontains')
            if word and not recursive:
                words = [x.name for x in contents.model.objects.filter(
                                                            **self.filters)]
                self.recommended_field = 'name__icontains'
            elif word_cities and not recursive:
                words = [x.name for x in BaseCity.objects.filter(
                                                        **self.filters)]
                word = word_cities
                self.recommended_field = 'location__cities__name__icontains'
            else:
                words = []
            words = list(set(words).union(
                                self._split_recommended_words(words)))
            recommended_words = searcher_words(query=word, words=words)
            if not word in dict(recommended_words).values():
                self._recommended_other_words = recommended_words
            else:
                self.recommended_other_words(contents, recursive=True)

    def _split_recommended_words(self, words):
        s = set()
        for phrase in words:
            word_list = phrase.split()
            if len(word_list) > 1:
                s = s.union(set(
                        [word for word in word_list if len(word) > 3]))
        return s

    def get_words_recommended(self):
        return self._recommended_other_words


def register_search_forms():
    search_form_registry.register_form(
        PlacesQuickSearchForm,
        name=_(u'Places Quick Search Form'),
        )
    search_form_registry.register_form(
        PlacesAdvancedSearchForm,
        name=_(u'Places Advanced Search Form'),
        )
