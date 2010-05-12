from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import FieldError
from django.forms.forms import BoundField
from django.forms.models import save_instance
from django.http import HttpResponse, Http404
from django.template import RequestContext, Template
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.text import capfirst
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent
from cmsutils.adminfilters import QueryStringManager
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


def _get_tabs(self):
    if not self.tabs:
        yield dict(name=None, fields=self)
    else:
        for tab, fieldsets in self.tabs:
            tabs_dict = dict(name=tab, fieldsets=[])
            for fieldset, fields in fieldsets:
                fieldset_dict = dict(name=fieldset, fields=[])
                for field_name in fields:
                    if field_name in self.fields.keyOrder:
                        fieldset_dict['fields'].append(self[field_name])
                if not fieldset_dict['fields']:
                    # if there is no fields in this fieldset, we continue to next fieldset
                    continue
                tabs_dict['fieldsets'].append(fieldset_dict)
            yield tabs_dict


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


class FormRequiredFields(object):

    required_css_class = 'required'

    def as_table_required(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output_required(
            normal_row = u'<tr%(html_class_attr)s><th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td></tr>',
            error_row = u'<tr><td colspan="2">%s</td></tr>',
            row_ender = u'</td></tr>',
            help_text_html = u'<br />%s',
            errors_on_separate_row = False)

    def as_ul_required(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output_required(
            normal_row = u'<li%(html_class_attr)s>%(errors)s%(label)s %(field)s%(help_text)s</li>',
            error_row = u'<li>%s</li>',
            row_ender = '</li>',
            help_text_html = u' %s',
            errors_on_separate_row = False)

    def as_p_required(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output_required(
            normal_row = u'<p%(html_class_attr)s>%(label)s %(field)s%(help_text)s</p>',
            error_row = u'%s',
            row_ender = '</p>',
            help_text_html = u' %s',
            errors_on_separate_row = True)

    def css_classes(self, extra_classes=None):
        """
        Returns a string of space-separated CSS classes for this field.
        """
        if hasattr(extra_classes, 'split'):
            extra_classes = extra_classes.split()
        extra_classes = set(extra_classes or [])
        if self.errors and hasattr(self.form, 'error_css_class'):
            extra_classes.add(self.form.error_css_class)
        if self.field.required and hasattr(self.form, 'required_css_class'):
            extra_classes.add(self.form.required_css_class)
        return ' '.join(extra_classes)

    def _html_output_required(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        "Helper function for outputting HTML. Used by as_table(), as_ul(), as_p()."
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []

        for name, field in self.fields.items():
            html_class_attr = ''
            bf = BoundField(self, field, name)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                # Create a 'class="..."' atribute if the row should have any
                # CSS classes applied.
                html_class_attr = ''
                if field.required:
                    html_class_attr = ' class="%s"' % self.required_css_class

                if errors_on_separate_row and bf_errors:
                    output.append(error_row % force_unicode(bf_errors))

                if bf.label:
                    label = conditional_escape(force_unicode(bf.label))
                    # Only add the suffix if the label does not end in
                    # punctuation.
                    if self.label_suffix:
                        if label[-1] not in ':?.!':
                            label += self.label_suffix
                    label = bf.label_tag(label) or ''
                else:
                    label = ''

                if field.help_text:
                    help_text = help_text_html % force_unicode(field.help_text)
                else:
                    help_text = u''

                output.append(normal_row % {
                    'errors': force_unicode(bf_errors),
                    'label': force_unicode(label),
                    'field': unicode(bf),
                    'help_text': help_text,
                    'html_class_attr': html_class_attr,
                })

        if top_errors:
            output.insert(0, error_row % force_unicode(top_errors))

        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                if not last_row.endswith(row_ender):
                    # This can happen in the as_p() case (and possibly others
                    # that users write): if there are only top errors, we may
                    # not be able to conscript the last row for our purposes,
                    # so insert a new, empty row.
                    last_row = (normal_row % {'errors': '', 'label': '',
                                              'field': '', 'help_text': '',
                                              'html_class_attr': html_class_attr})
                    output.append(last_row)
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe(u'\n'.join(output))


class FormTabs(object):
    """
    Abstract class implemented to provide form with tabs like
    Usage::

       class FooForm(forms.Form, FormTabs):
          tabs = (
                  ({'name': _(tab1_name), 'title': _(tab1_title)}, (
                        (_(accordion1),
                            (fiel1d, field2, ... )),
                        (_(accordion2), ...)
                    ),
                ),
                ...
            )
    """
    tabs = ()
    get_tabs = property(_get_tabs)

    class Media:
        js = (
              settings.MEDIA_URL + "merengue/js/formtabs/jquery-ui-1.6.custom.min.js",
              settings.MEDIA_URL + "merengue/js/formtabs/formtabs_initial.js",
             )
        css = {'all': (settings.MEDIA_URL + "merengue/css/formtabs/ui-lightness/ui.all.css",
                      )}

    def as_tab(self):
        return render_to_string('base/formtabs.html', {'form': self, })


class BaseForm(forms.Form, FormRequiredFields):
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


class BaseModelForm(forms.ModelForm, FormAdminDjango, FormRequiredFields):
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

    # Search Interface
    results_template = 'base/search_results_view.html'
    base_results_template = 'section/base_section.html'
    results_model = None

    def get_selected_menu(self):
        return "%s-searcher" % self.results_model._meta.module_name

    def get_results_queryset(self, request):
        return self.results_model.objects.published()

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

    def render_search_results_map(self, request):
        results = self.search_results(request)
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
            )
    )

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
        )
    )

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
