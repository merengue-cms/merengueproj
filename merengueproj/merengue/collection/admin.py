from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from transmeta import get_real_fieldname_in_each_language

from merengue.base.admin import (BaseContentAdmin, RelatedModelAdmin,
                                 BaseOrderableAdmin)
from merengue.section.admin import SectionContentAdmin

from merengue.base.models import BaseContent
from merengue.section.models import Section
from merengue.collection.models import (Collection, IncludeCollectionFilter,
                                        ExcludeCollectionFilter,
                                        CollectionDisplayField,
                                        CollectionDisplayFieldFilter)
from merengue.collection.utils import get_common_fields_no_language, \
                                                            get_common_fields
from merengue.collection.forms import CollectionFilterForm


DEFAULT_FILTERS = (
    ('', ''),
    ('django.template.defaultfilters.truncatewords', _('Truncate words'), ),
    ('django.template.defaultfilters.truncatewords_html', _('Truncate words HTML'), ),
    ('cmsutils.templatetags.stringfilters.truncatechars', _('Truncate chars'), ),
)


class CollectionFilterInline(admin.TabularInline):
    """
    Inline admin interface for editing queryset filters.
    """

    form = CollectionFilterForm

    def get_default_fields(self, obj):
        if not obj:
            return []
        return [('', '----------')] + [(i, i) for i in get_common_fields(obj)]

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(CollectionFilterInline, self).get_formset(request, obj, **kwargs)
        form = formset.form
        default_fields = self.get_default_fields(obj)
        if default_fields:
            default_fields += [('content_type_name', 'content_type_name')]
            default_fields.sort()
        for i in ('filter_field', 'field_name'):
            if i in form.base_fields:
                form.base_fields[i].widget = forms.Select(choices=default_fields)
        return formset


class ExcludeCollectionFilterInline(CollectionFilterInline):
    model = ExcludeCollectionFilter


class IncludeCollectionFilterInline(CollectionFilterInline):
    model = IncludeCollectionFilter


class CollectionAdmin(BaseContentAdmin):
    fieldsets = (
        (_('Collection Basic Information'),
            {'fields': get_real_fieldname_in_each_language('name') +\
                       ['slug', ] +\
                       get_real_fieldname_in_each_language('description') +\
                       ['status', 'tags', 'meta_desc', 'commentable', 'owners']},
            ),
        (_('Collection Configuration'),
            {'fields': ('content_types', 'group_by', 'order_by', 'reverse_order', 'show_main_image')},
            ),
        )
    filter_horizontal = BaseContentAdmin.filter_horizontal + ('content_types', )
    inlines = [IncludeCollectionFilterInline, ExcludeCollectionFilterInline]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        media = context.get('media')
        media += mark_safe(forms.Media(js=['%smerengue/js/collection/SelectBox.js' % settings.MEDIA_URL,
                                           '%smerengue/js/collection/jquery.collection-admin.js' % settings.MEDIA_URL]))
        context.update({'media': media})
        return super(CollectionAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def get_default_fields(self, obj):
        if not obj:
            return []
        return [('', '----------')] + [(i, i) for i in get_common_fields_no_language(obj)]

    def get_subclasses(self, cls_list, _seen=None):
        ## {{{ http://code.activestate.com/recipes/576949/ (r3)
        for cls in cls_list:
            if not isinstance(cls, type):
                raise TypeError('itersubclasses must be called with '
                                'new-style classes, not %.100r' % cls)
            if _seen is None:
                _seen = set()
            try:
                subs = cls.__subclasses__()
            except TypeError:  # fails only when cls is type
                subs = cls.__subclasses__(cls)
            for sub in subs:
                if sub not in _seen:
                    _seen.add(sub)
                    yield sub
                    for sub in self.get_subclasses([sub], _seen):
                        yield sub

    def get_form(self, request, obj=None, **kwargs):
        form = super(CollectionAdmin, self).get_form(request, obj, **kwargs)
        if 'content_types' in form.base_fields:
            main_models = self.get_subclasses([BaseContent, Section])
            types_id = []
            for m in main_models:
                if not m._meta.abstract:
                    types_id.append(ContentType.objects.get_for_model(m).id)
            form.base_fields['content_types'].queryset = form.base_fields['content_types'].queryset.filter(id__in=types_id)
        default_fields = self.get_default_fields(obj)
        if default_fields:
            default_fields += [('content_type_name', 'content_type_name')]
            default_fields.sort()
        for i in ('group_by', 'order_by'):
            if i in form.base_fields:
                form.base_fields[i].widget = forms.Select(choices=default_fields)
        return form


class CollectionRelatedModelAdmin(SectionContentAdmin, CollectionAdmin):
    tool_name = 'collections'
    tool_label = _('collections')


class CollectionDisplayFieldFilterInline(admin.TabularInline):
    model = CollectionDisplayFieldFilter

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(CollectionDisplayFieldFilterInline, self).get_formset(request, obj, **kwargs)
        form = formset.form
        if 'filter_module' in form.base_fields:
            form.base_fields['filter_module'].widget = forms.Select(choices=DEFAULT_FILTERS)
        return formset


class CollectionDisplayFieldAdmin(RelatedModelAdmin, BaseOrderableAdmin):
    tool_name = 'display_fields'
    tool_label = _('display fields')
    related_field = 'collection'
    sortablefield = 'field_order'
    ordering = ('field_order', )
    exclude = ('field_order', )
    list_display = ('__unicode__', 'safe', 'show_label')

    inlines = [CollectionDisplayFieldFilterInline]

    def get_default_fields(self, obj):
        if not obj:
            return []
        return [('', '----------')] + [(i, i) for i in get_common_fields_no_language(obj)]

    def save_model(self, request, obj, form, change):
        if not change:
            fields = obj.collection.display_fields.all().order_by('-field_order')
            if not fields:
                obj.field_order = 0
            else:
                obj.field_order = fields[0].field_order + 1
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super(CollectionDisplayFieldAdmin, self).get_form(request, obj, **kwargs)

        default_fields = self.get_default_fields(self.basecontent)
        if default_fields:
            default_fields += [('content_type_name', 'content_type_name')]
            default_fields.sort()
        for i in ('filter_field', 'field_name'):
            if i in form.base_fields:
                form.base_fields[i].widget = forms.Select(choices=default_fields)
        return form


def register_related(site):
    site.register_related(Collection, CollectionRelatedModelAdmin, related_to=Section)
    site.register_related(CollectionDisplayField, CollectionDisplayFieldAdmin, related_to=Collection)


def register(site):
    site.register(Collection, CollectionAdmin)
    register_related(site)
