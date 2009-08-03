# -*- coding: utf-8 -*-
import datetime
import time

from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from cmsutils.templatetags.datefilters import get_date_format

from base.forms import QuickSearchForm, AdvancedSearchForm
from certificate.forms import UniqueCertificateSearchTerm
from searchform.registry import search_form_registry
from searchform.terms import TextSearchTerm, FreeTextSearchTerm, DateSearchTerm, ObjectsSearchTerm

from places.terms import (CityQuickSearchTerm, CitySearchTerm,
                          ProvinceQuickSearchTerm, ProvinceSearchTerm,
                          TouristZoneSearchTerm, BindableSearchTerm)
from event.models import CategoryGroup, Category, Event


class EventCategorySearchTerm(BindableSearchTerm, ObjectsSearchTerm):
    model = Category


class EventCategoryQuickSearchTerm(EventCategorySearchTerm):
    searchlet_type = 'checkbox_options'
    template = 'search/checkbox_search_term.html'


class EventTypeSearchTerm(BindableSearchTerm, ObjectsSearchTerm):
    model = CategoryGroup


class EventTypeQuickSearchTerm(EventTypeSearchTerm):
    searchlet_type = 'checkbox_options'
    template = 'search/checkbox_search_term.html'

    def queryset(self):
        return super(EventTypeQuickSearchTerm, self).queryset().filter(
            hidden_in_global_search=False,
        )


class EventDateInRange(DateSearchTerm):
    template = "search/single_date_search_term_for_range.html"
    searchlet_type = "singledate"
    date_formats = {'es': '%d/%m/%Y',
                    'default': '%Y-%m-%d',
                   }

    def render_searchlet_block(self):
        options = [{'operator': op, 'label': label}
                   for op, label in self.operators]
        context = {
            'field': self,
            'options': options,
            'language': get_language(),
            'format': self.date_formats.get(get_language(), self.date_formats['default']),
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
            'MEDIA_URL': settings.MEDIA_URL,
            }
        return render_to_string(self.template, context)

    def get_query_arg_as_text(self, operator, value):
        date = datetime.date(*time.strptime(value, '%Y-%m-%d')[:3])
        localized_date = date.strftime(get_date_format('short'))
        return u'%s %s' % (self.get_description(operator), localized_date)


class EventDateSearchTerm(DateSearchTerm):
    operators = (
        ('exact', _('is exactly')),
        ('gte', _('greater than')),
        ('lte', _('less than')))
    searchlet_type = "datei10n"

    def get_query_arg_as_text(self, operator, value):
        date = datetime.date(*time.strptime(value, '%Y-%m-%d')[:3])
        localized_date = date.strftime(get_date_format('short'))
        return u'%s %s' % (self.get_description(operator), localized_date)


class EventFromDateQuickSearchTerm(EventDateSearchTerm):
    operators = (
        ('gte', _('from')), )
    operator = operators[0][0]
    operator_label = operators[0][1]
    template = "search/single_date_search_term.html"
    searchlet_type = "singledate"


class EventToDateQuickSearchTerm(EventDateSearchTerm):
    operators = (
        ('lte', _('to')), )
    operator = operators[0][0]
    operator_label = operators[0][1]
    template = "search/single_date_search_term.html"
    searchlet_type = "singledate"


class CertificateEventSearchTerm(UniqueCertificateSearchTerm):
    class_name = 'event'


COMMON_FIELDS = [
        ('name',
            FreeTextSearchTerm(_(u'Name'),
                            _(u'Name'),
                            _(u'which name'))),

        ('location__cities__name',
            FreeTextSearchTerm(_(u'City'),
                            _(u'City'),
                            _(u'which city'))),

        ('location__cities',
            CityQuickSearchTerm(_(u'City'),
                                _(u'City'),
                                _(u'which city'))),

        ('location__cities__province',
            ProvinceQuickSearchTerm(_(u'Province'),
                                    _(u'Province'),
                                    _(u'which province'))),

        ('cached_max_end__gte',
        EventDateInRange(_(u'From'),
                            _(u'From'),
                            _(u'From'))),

        ('cached_min_start__lte',
            EventDateInRange(_(u'To'),
                            _(u'To'),
                            _(u'To'))),
]


class BaseEventSearchForm(object):

    results_model = Event
    results_template = 'event/search_results_view.html'

    def get_results_queryset(self, request):
        filters = {}
        order_by = ('cached_min_start', )
        now = datetime.datetime.now()
        start = request.GET.get('cached_max_end__gte', None)
        end = request.GET.get('cached_min_start__lte', None)
        name = request.GET.get('name__icontains', '')

        if end:
            try:
                (year, month, day) = end.split("-")
                end = datetime.datetime(int(year), int(month), int(day))
            except ValueError:
                end = now

        if ((name and not (start or end)) or
            (not start and end and end < now) or
            (start and end)):
            queryset = Event.objects.allpublished()
        elif not start and end and end >= now:
            queryset = Event.objects.published()
        else:
            queryset = Event.objects.published()

        return queryset.filter(**filters).order_by(*order_by)


class EventComunQuickSearchForm(BaseEventSearchForm, QuickSearchForm):
    title = _(u'Events calendar')
    use_tabs = False
    extra_scripts = QuickSearchForm.extra_scripts + (
        '%sjs/event_quick_search.js' % settings.MEDIA_URL,
        '%sjs/dates_l10n/dates_l10n.js' % settings.MEDIA_URL,
        '%sjs/core.js' % settings.ADMIN_MEDIA_PREFIX,
        #'%sjs/calendar.js' % settings.ADMIN_MEDIA_PREFIX,
        '%sjscalendar/calendar.js' % settings.MEDIA_URL,
        '%sjscalendar/calendar-setup.js' % settings.MEDIA_URL,
        #'%sjs/DateTimeShortcuts.js' % settings.MEDIA_URL,
        )
    template = 'event/quick_search_form.html'

    def render_media(self):
        self.extra_scripts = self.extra_scripts + ('%sjs/dates_l10n/dates_l10n_%s.js' % (settings.MEDIA_URL, get_language()), )
        return super(EventComunQuickSearchForm, self).render_media()


class EventQuickSearchForm(EventComunQuickSearchForm):

    fields = SortedDict(COMMON_FIELDS +
                                        [('categories__groups',
                                            EventTypeQuickSearchTerm(_(u'The event group type'),
                                            _(u'The event group type'),
                                            _(u'which type'))), ])


class EventCategoriesQuickSearchForm(EventComunQuickSearchForm):

    template = 'event/event_category_quick_search_form.html'
    title = _(u"Agenda")

    fields = SortedDict(COMMON_FIELDS +
                                        [('categories',
                                             EventCategoryQuickSearchTerm(_(u'The event type'),
                                            _(u'The event type'),
                                            _(u'which type'))), ])

    def __init__(self, section, *args, **kwargs):
        super(EventCategoriesQuickSearchForm, self).__init__(*args, **kwargs)
        if section:
            self.section = section
            self.fields['categories'].filters = {'id__in': EventCategoriesQuickSearchForm.get_categories(section).values('pk').query}

    @classmethod
    def get_categories(cls, section):
        return Category.objects.filter(Q(sections__in=[section]) | Q(groups__sections__in=[section])).distinct()

    results_model = Event
    results_template = 'section/search_results_view.html'

    def get_results_queryset(self, request):
        filters = {}
        order_by = ('cached_min_start', )
        now = datetime.datetime.now()
        start = request.GET.get('cached_max_end__gte', None)
        end = request.GET.get('cached_max_end__lte', None)
        name = request.GET.get('name__icontains', '')

        categories = request.GET.get('categories__in', None)

        if not categories:
            categories_query = EventCategoriesQuickSearchForm.get_categories(self.section)
            filters['categories__in'] = categories_query.values('pk').query

        if (name or
            (start and end) or
            (end and not name)):
            queryset = Event.objects.allpublished()
        else:
            queryset = Event.objects.published()

        return queryset.filter(**filters).order_by(*order_by)


class EventAdvancedSearchForm(BaseEventSearchForm, AdvancedSearchForm):
    title = _(u'Events calendar')
    extra_scripts = AdvancedSearchForm.extra_scripts + (
        '%sjs/dates_l10n/dates_l10n.js' % settings.MEDIA_URL,
        '%sjs/core.js' % settings.ADMIN_MEDIA_PREFIX,
        )

    fields = SortedDict((
            ('name',
             TextSearchTerm(_(u'Name'),
                                _(u'Name'),
                                _(u'which name'))),

            ('location__cities',
             CitySearchTerm(_(u'City'),
                            _(u'City'),
                            _(u'which city'))),

            ('location__cities__province',
             ProvinceSearchTerm(_(u'Province'),
                                _(u'Province'),
                                _(u'which province'))),

            ('location__cities__touristzone',
             TouristZoneSearchTerm(_(u'The tourist Zone'),
                                   _(u'Tourist Zone'),
                                   _(u'which tourist zone'))),

            ('categories__groups',
             EventTypeSearchTerm(_(u'Event type'),
                                      _(u'Type'),
                                      _(u'which type'))),

            ('certificates',
                CertificateEventSearchTerm(_(u'Quality mark'),
                                           _(u'Quality mark'),
                                           _(u'which quality mark'))),

            ('cached_min_start',
             EventDateSearchTerm(_(u'From'),
                                 _(u'From'),
                                 _(u'From'))),

            ('cached_max_end',
             EventDateSearchTerm(_(u'To'),
                                 _(u'To'),
                                 _(u'To'))),

            ))

    def render_media(self):
        self.extra_scripts = self.extra_scripts + ('%sjs/dates_l10n/dates_l10n_%s.js' % (settings.MEDIA_URL, get_language()), )
        return super(EventAdvancedSearchForm, self).render_media()


def register_search_forms():
    search_form_registry.register_form(
        EventQuickSearchForm,
        name=_(u'Event Quick Search Form'),
        )
    search_form_registry.register_form(
        EventCategoriesQuickSearchForm,
        name=_(u'Event Categories Quick Search Form'),
        )
    search_form_registry.register_form(
        EventAdvancedSearchForm,
        name=_(u'Event Advanced Search Form'),
        )
