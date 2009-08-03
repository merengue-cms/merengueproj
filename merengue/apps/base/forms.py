from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import FieldError
from django.forms.models import save_instance
from django.http import HttpResponse, Http404
from django.template import RequestContext, Template
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.text import capfirst
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from base.models import BaseContent
from base.searchterms import FeatureSearchTerm, HandicapedSearchTerm
from certificate.forms import CertificateQuickSearchTerm
from cmsutils.adminfilters import QueryStringManager
from places.terms import CityQuickSearchTerm, ProvinceQuickSearchTerm
from places.terms import CitySearchTerm, ProvinceSearchTerm, TouristZoneSearchTerm
from places.terms import CertificateResourceSearchTerm, ContentClassSearchTerm
from places.models import City
from searchform.forms import SearchForm
from searchform.registry import search_form_registry
from searchform.terms import FreeTextSearchTerm, TextSearchTerm
from transmeta import canonical_fieldname

from threadedcomments.models import FreeThreadedComment
from threadedcomments.forms import FreeThreadedCommentForm
from captcha.fields import CaptchaField


def _get_fieldsets(self):
    if not self.fieldsets:
        yield dict(name=None, fields=self)
    else:
        for fieldset, fields in self.fieldsets:
            fieldset_dict = dict(name=fieldset, fields=[])
            for field_name in fields:
                if field_name in self.fields.keyOrder:
                    fieldset_dict['fields'].append(self[field_name])
            if not fieldset_dict['fields']:
                # if there is no fields in this fieldset, we continue to next fieldset
                continue
            yield fieldset_dict


def _as_div(self):
    "Returns this form rendered as HTML <div>s."
    return render_to_string('base/baseform.html', {'form': self})


class FormAdminDjango(object):
    """
    Abstract class implemented to provide form django admin like
    Usage::

       class FooForm(forms.Form, FormAdminDjango):
          ...
    """

    def as_django_admin(self):
        return render_to_string('base/form_admin_django.html', {'form': self, })


class BaseForm(forms.Form):
    fieldsets = ()
    two_columns_fields = ()
    three_columns_fields = ()
    get_fieldsets = property(_get_fieldsets)

    def __unicode__(self):
        return self.as_div()

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        instance=kwargs.get('instance', None)
        for name, field in self.fields.items():
            if name in self.two_columns_fields:
                field.column_style = 'twoColumnsField'
            elif name in self.three_columns_fields:
                field.column_style = 'threeColumnsField'

    as_div = _as_div


class BaseModelForm(forms.ModelForm, FormAdminDjango):
    fieldsets = ()
    two_columns_fields = ()
    three_columns_fields = ()
    get_fieldsets = property(_get_fieldsets)

    def _add_transmeta_fields(self, instance):
        opts = self._meta
        lang = get_language()
        if opts.model:
            field_list = []
            modelopts = opts.model._meta
            transmeta_fields = [f for f in modelopts.fields if canonical_fieldname(f)!=f.name]
            for f in transmeta_fields:
                if not f.editable:
                    continue
                if opts.fields and not canonical_fieldname(f) in opts.fields:
                    continue
                if opts.exclude and canonical_fieldname(f) in opts.exclude:
                    continue
                if not f.name.endswith('_'+lang):
                    continue
                formfield = f.formfield()
                formfield.label = capfirst(_(canonical_fieldname(f)))
                formfield.lang_name = f.name
                if instance and not canonical_fieldname(f) in self.initial.keys():
                    self.initial.update({canonical_fieldname(f): f.value_from_object(instance)})
                if formfield:
                    field_list.append((canonical_fieldname(f), formfield))
            self.transmeta_fields=SortedDict(field_list)
            self.fields.update(self.transmeta_fields)
            if opts.fields:
                order = [fieldname for fieldname in opts.fields if fieldname in self.fields.keys()]
                self.fields.keyOrder=order

    def clean(self):
        cleaned_data = super(BaseModelForm, self).clean()
        if cleaned_data:
            for name, f in self.transmeta_fields.items():
                if name in cleaned_data.keys():
                    cleaned_data.update({f.lang_name: cleaned_data.get(name)})
        return cleaned_data

    def save(self, commit=True):
        if self.instance.pk is None:
            fail_message = 'created'
        else:
            fail_message = 'changed'
        transmeta_field_names = [f.lang_name for f in self.transmeta_fields.values()]
        default_fields = (self._meta.fields and list(self._meta.fields)) or []
        return save_instance(self, self.instance, default_fields + transmeta_field_names, fail_message, commit)

    def __init__(self, *args, **kwargs):
        super(BaseModelForm, self).__init__(*args, **kwargs)
        instance=kwargs.get('instance', None)
        self._add_transmeta_fields(instance)
        for name, field in self.fields.items():
            if name in self.two_columns_fields:
                field.column_style = 'twoColumnsField'
            elif name in self.three_columns_fields:
                field.column_style = 'threeColumnsField'

    def __unicode__(self):
        return self.as_div()

    as_div = _as_div


class CaptchaFreeThreadedCommentForm(BaseModelForm, FreeThreadedCommentForm):

    class Meta:
        model = FreeThreadedComment
        fields = ('comment', 'name', 'website', 'email', )

    def __init__(self, user, *args, **kwargs):
        super(CaptchaFreeThreadedCommentForm, self).__init__(*args, **kwargs)
        if user.is_anonymous():
            captcha_field = CaptchaField()
            self.fields['captcha'] = captcha_field
            self.declared_fields['captcha'] = captcha_field


class AdminBaseContentOwnersForm(forms.Form):

    owners = forms.ModelMultipleChoiceField(User.objects.all(), widget=FilteredSelectMultiple(_('owners'), False))

    class Media:
        js = ("/jsi18n/",
              settings.ADMIN_MEDIA_PREFIX + "js/core.js",
              settings.ADMIN_MEDIA_PREFIX + "js/SelectBox.js",
              settings.ADMIN_MEDIA_PREFIX + "js/SelectFilter2.js",
             )
        css = {'all': (settings.ADMIN_MEDIA_PREFIX + "css/forms.css",
                       settings.MEDIA_URL + "css/admin.css",
                      )}


class TransTextSearchTerm(TextSearchTerm):

    def _field_name_with_language(self, field_name):
        return '%s_%s' % (field_name, get_language())

    def bind(self, field_name):
        return super(TransTextSearchTerm, self).bind(self._field_name_with_language(field_name))


def add_villages_to_city(filters):
    """Add the villages of a city when the filter includes that city.

    Example: if the filters includes this:

       location__cities__exact=23

    the new filter is

       location__cities__in=[23, 45, 31]

    Where 45 and 31 are villages which city is 23

    Note: this function MODIFIES (like all filters processors)
    the filters argument.
    """
    new_filters = filters
    if 'location__cities__exact' in filters:
        city_id = int(filters['location__cities__exact'])
        try:
            city = City.objects.get(id=city_id)
            villages = [v.id for v in city.villages.all()]
            new_filters = filters
            new_filters['location__cities__in'] = [city_id] + villages
            del new_filters['location__cities__exact']
        except City.DoesNotExist:
            pass # it was already a village

    return new_filters


class BaseSearchForm(SearchForm):

    extra_scripts = ('%sjs/searchlets.js' % settings.MEDIA_URL, )

    @classmethod
    def class_name(cls):
        return cls.__name__.lower()

    @classmethod
    def content_name(cls):
        class_name = cls.class_name
        if 'quicksearchform' in class_name:
            return class_name.split('quicksearchform')[0]
        elif 'advancedsearchform' in class_name:
            return class_name.split('advancedsearchform')[0]
        return class_name

    @classmethod
    def title(cls):
        return cls.content_name().capitalize()

    def __init__(self, *args, **kwargs):
        super(BaseSearchForm, self).__init__(*args, **kwargs)
        if 'features' in self.fields:
            self.fields['features'].filters = {'basecontent__class_name': self.content_name()}
        if 'handicapped_services' in self.fields:
            self.fields['handicapped_services'].filters = {'basecontent__class_name': self.content_name()}

        # Ver #1912. Cuando los contenidos esten bien rellenados esto sera redundante
        if 'certificates' in self.fields:
            if len(self.fields['certificates'] .options) == 0:
                del self.fields['certificates']


    # Search Interface
    results_template = 'base/search_results_view.html'
    base_results_template = 'section/base_section.html'
    results_model = None

    def get_selected_menu(self):
        return "%s-searcher" % self.results_model._meta.module_name

    def get_results_queryset(self, request):
        return self.results_model.objects.published()

    def get_filter_processors(self):
        # add villages to the cities filter so we include
        # the village's resources when searching its city
        return [add_villages_to_city]

    def get_select_related_fields(self):
        # prefetch the location since we draw a mini google map for each hit
        return ['location']

    def filter_by_query_string(self, request, queryset, page_var='p',
                               search_fields=[], none_if_empty=False,
                               filter_processors=[]):
        qsm = QueryStringManager(request, search_fields, page_var)
        filters = qsm.get_filters()
        excluders = qsm.get_excluders()
        if filters or excluders:
            try:
                new_filters = dict(filters)
                for processor in filter_processors:
                    processor(new_filters)

                queryset = queryset.filter(**new_filters)
                queryset = queryset.exclude(**excluders)
            except FieldError, e:
                raise Http404
        elif none_if_empty:
            queryset = queryset.none()

        return queryset, qsm

    def search_results(self, request):
        queryset = self.get_results_queryset(request)

        filter_processors = self.get_filter_processors()
        results, qsm = self.filter_by_query_string(request, queryset,
                                                   none_if_empty=True,
                                                   page_var=settings.PAGE_VARIABLE,
                                                   filter_processors=filter_processors)

        select_related_fields = self.get_select_related_fields()
        if select_related_fields:
            results = results.select_related(*select_related_fields).distinct()
        else:
            results = results.distinct()

        self.set_qsm(qsm)

        return results

    @property
    def results_class_name(self):
        """Used when filtering the cities using the province select"""
        if self.results_model:
            return self.results_model._meta.module_name

    def render_search_results_map(self, request):
        results = self.search_results(request)
        #import ipdb; ipdb.set_trace()
        context = RequestContext(request, {'object_list': results})
        template = Template("""
        {% load i18n map_tags %}
        <div class="contentMap">
        {% google_map content_pois=object_list %}
        {% if object_list|localized %}
           {% google_map_proximity_filter %}
        {% else %}
           <p class="infomsg"><strong>{% trans "Sorry, there is no localized objects" %}</strong></p>
        {% endif %}
        </div>
        """)
        return HttpResponse(template.render(context))


class QuickSearchForm(BaseSearchForm):
    search_type = 'quick'
    use_tabs = False


class AdvancedSearchForm(BaseSearchForm):
    search_type = 'advanced'
    template = 'base/searchform.html'
    use_tabs = True


services_advanced_fields = (
    ('features', FeatureSearchTerm(_(u'Feature'),
                                   _(u'Feature'),
                                   _(u'which feature'))),
    ('handicapped_services', HandicapedSearchTerm(_(u'Handicapped services'),
                                                  _(u'Handicapped services'),
                                                  _(u'which handicapped services'))),
    )


class BaseBaseContentSearchForm(object):

    results_model = BaseContent
    base_results_template = 'section/base_section.html'


class BaseContentQuickSearchForm(BaseBaseContentSearchForm, QuickSearchForm):

    title = _('Base contents')
    break_navigation = True
    template = 'base/basecontent_quick_search_form.html'

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

            ('location__cities__province',
             ProvinceQuickSearchTerm(_(u'Province'),
                                     _(u'Province'),
                                     _(u'which province'))),

            ('certificates',
             CertificateQuickSearchTerm(_(u'Quality mark'),
                                        _(u'Quality mark'),
                                        _(u'which quality mark'))),

            ('class_name',
             ContentClassSearchTerm(_(u'Type'),
                                    _(u'Type'),
                                    _(u'which type'))),

            ))

    def __init__(self, *args, **kwargs):
        super(BaseContentQuickSearchForm, self).__init__(*args, **kwargs)
        if 'features' in self.fields:
            del self.fields['features'].filters['basecontent__class_name']
        if 'handicapped_services' in self.fields:
            del self.fields['handicapped_services'].filters['basecontent__class_name']


class BaseContentAdvancedSearchForm(BaseBaseContentSearchForm, AdvancedSearchForm):

    title = _('Base contents')
    fields = SortedDict((
            ('name',
             TextSearchTerm(_(u'Name'),
                            _(u'Name'),
                            _(u'which name'))),

            ('location__cities',
             CitySearchTerm(_(u'The city'),
                            _(u'City'),
                            _(u'which city'))),

            ('location__cities__province',
             ProvinceSearchTerm(_(u'Province'),
                                _(u'Province'),
                                _(u'which province'))),

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


            ) + services_advanced_fields)

    def __init__(self, *args, **kwargs):
        super(BaseContentAdvancedSearchForm, self).__init__(*args, **kwargs)
        if 'features' in self.fields:
            del self.fields['features'].filters['basecontent__class_name']
        if 'handicapped_services' in self.fields:
            del self.fields['handicapped_services'].filters['basecontent__class_name']


def register_search_forms():
    search_form_registry.register_form(
        BaseContentQuickSearchForm,
        name=_(u'Base Content Quick Search Form'),
        )
    search_form_registry.register_form(
        BaseContentAdvancedSearchForm,
        name=_(u'Base Content Advanced Search Form'),
        )
