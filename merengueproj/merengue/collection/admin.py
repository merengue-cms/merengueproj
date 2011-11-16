# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from transmeta import get_real_fieldname_in_each_language

from merengue.base.admin import (BaseContentAdmin, RelatedModelAdmin,
                                 BaseOrderableAdmin)
from merengue.base.forms import BaseAdminModelForm
from merengue.section.admin import SectionContentAdmin

from merengue.base.models import BaseContent
from merengue.section.models import BaseSection
from merengue.collection.forms import (CollectionFilterForm, CollectionDisplayFilterForm,
                                       CollectionAdminModelForm)
from merengue.collection.models import (Collection, IncludeCollectionFilter,
                                        ExcludeCollectionFilter,
                                        CollectionDisplayField,
                                        CollectionDisplayFieldFilter,
                                        FeedCollection, FeedItem)
from merengue.collection.utils import get_common_fields_no_language, get_common_fields


DEFAULT_FILTERS = (
    ('', ''),
    ('django.template.defaultfilters.truncatewords', _('Truncate words'), ),
    ('django.template.defaultfilters.truncatewords_html', _('Truncate words HTML'), ),
    ('cmsutils.templatetags.stringfilters.truncatechars', _('Truncate chars'), ),
    ('django.template.defaultfilters.striptags', _('Strip tags'), ),
)


class CollectionFilterInline(admin.TabularInline):
    """
    Inline admin interface for editing queryset filters.
    """

    form = CollectionFilterForm

    def get_default_fields(self, obj, request):
        if not obj:
            return [('', '----------')] + [(i, i) for (k, i) in request.POST.items() if k.endswith('filter_field')]
        return [('', '----------')] + [(i, i) for i in get_common_fields(obj)]

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(CollectionFilterInline, self).get_formset(request, obj, **kwargs)
        form = formset.form
        default_fields = self.get_default_fields(obj, request)
        if default_fields:
            default_fields += [('content_type_name', 'content_type_name')]
            default_fields.sort()
        if 'filter_field' in form.base_fields:
            form.base_fields['filter_field'].widget = forms.Select(choices=default_fields)
        return formset


class ExcludeCollectionFilterInline(CollectionFilterInline):
    model = ExcludeCollectionFilter


class IncludeCollectionFilterInline(CollectionFilterInline):
    model = IncludeCollectionFilter


class CollectionAdmin(BaseContentAdmin):
    filter_horizontal = BaseContentAdmin.filter_horizontal + ('content_types', )
    inlines = [IncludeCollectionFilterInline, ExcludeCollectionFilterInline]
    change_form_template = 'collection/collection_admin_change_form.html'
    form = CollectionAdminModelForm

    def get_title_basic_info_fields(self, request, obj=None):
        return _('Collection Basic Information')

    def get_basic_info_fields(self, request, obj=None):
        basic_info_fields = get_real_fieldname_in_each_language('name') + \
                            ['slug', ] + get_real_fieldname_in_each_language('description') + \
                            ['workflow_status', 'tags', 'meta_desc', 'commentable']
        if request.user.is_superuser:
            basic_info_fields.append('owners')
        return basic_info_fields

    def get_title_configurations_fields(self, request, obj=None):
        return _('Collection Configuration')

    def get_configurations_fields(self, request, obj=None):
        return ['content_types', 'group_by', 'order_by', 'reverse_order', 'limit',
                'show_main_image', 'filtering_section']

    def get_fieldsets(self, request, obj=None):
        return ((self.get_title_basic_info_fields(request, obj),
                {'fields': self.get_basic_info_fields(request, obj)}),
                (self.get_title_configurations_fields(request, obj),
                {'fields': self.get_configurations_fields(request, obj)}),)

    def queryset(self, request):
        qs = super(CollectionAdmin, self).queryset(request)
        return qs.filter(feedcollection__isnull=True)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        media = context.get('media')
        media += mark_safe(forms.Media(js=['%smerengue/js/collection/SelectBox.js' % settings.MEDIA_URL,
                                           '%smerengue/js/collection/jquery.collection-admin.js' % settings.MEDIA_URL]))
        context.update({'media': media})
        return super(CollectionAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def get_default_fields(self, obj, request):
        if not obj:
            return [('', '----------')] + [(i, i) for (k, i) in request.POST.items() if k.endswith('_by')]
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
                if issubclass(cls, BaseContent):
                    subs = cls.get_subclasses()
                else:
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
            main_models = self.get_subclasses([BaseContent, ])
            types_id = []
            for m in main_models:
                if not m._meta.abstract:
                    types_id.append(ContentType.objects.get_for_model(m).id)
            types_id.append(ContentType.objects.get_for_model(BaseContent).id)
            form.base_fields['content_types'].queryset = form.base_fields['content_types'].queryset.filter(id__in=types_id)
        default_fields = self.get_default_fields(obj, request)
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
    change_form_template = CollectionAdmin.change_form_template


class CollectionDisplayFieldFilterInline(admin.TabularInline):
    model = CollectionDisplayFieldFilter
    form = CollectionDisplayFilterForm

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(CollectionDisplayFieldFilterInline, self).get_formset(request, obj, **kwargs)
        form = formset.form
        if 'filter_module' in form.base_fields:
            form.base_fields['filter_module'].widget = forms.Select(choices=DEFAULT_FILTERS)
        return formset


class CollectionDisplayFieldAdmin(RelatedModelAdmin, BaseOrderableAdmin):
    tool_name = 'display_fields'
    tool_label = _('fields to display in the list')
    related_field = 'collection'
    sortablefield = 'field_order'
    ordering = ('field_order', )
    exclude = ('field_order', )
    list_display = ('__unicode__', 'safe', 'show_label')

    inlines = [CollectionDisplayFieldFilterInline]

    def queryset(self, request):
        qs = super(CollectionDisplayFieldAdmin, self).queryset(request)
        return qs.filter(list_field=True)

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
        if 'field_name' in form.base_fields:
            form.base_fields['field_name'].widget = forms.Select(choices=default_fields)
        return form


class FeedItemDisplayFieldAdmin(CollectionDisplayFieldAdmin):
    tool_name = 'display_fields_in_item'
    tool_label = _('fields in the detail view of the object')

    def get_default_fields(self, obj):
        if not obj:
            return []
        fields = []
        items = obj.feeditem_set.all()
        if items.count():
            first = items[0].get_full_item(obj.detailed_link)
            fields = first.keys()
        return [('', '----------')] + [(i, i) for i in fields]

    def queryset(self, request):
        qs = super(CollectionDisplayFieldAdmin, self).queryset(request)
        return qs.filter(list_field=False)

    def save_model(self, request, obj, form, change):
        obj.list_field = False
        super(FeedItemDisplayFieldAdmin, self).save_model(request, obj, form, change)


class FeedItemAdmin(RelatedModelAdmin):
    tool_name = 'items'
    tool_label = _('feed items')
    related_field = 'feed_collection'
    exclude = ('owners', 'participants', 'adquire_global_permissions')


class FeedCollectionAdmin(CollectionAdmin):
    change_form_inlines = [IncludeCollectionFilterInline, ExcludeCollectionFilterInline]
    form = BaseAdminModelForm
    item_fieldsets = (
        (_('Single Item Configuration'),
            {'fields': ('title_field', 'detailed_link', 'external_link', )},
            ),
        )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(FeedCollectionAdmin, self).get_fieldsets(request, obj)
        if obj:
            fieldsets = fieldsets + self.item_fieldsets
        return fieldsets

    def get_configurations_fields(self, request, obj=None):
        if not obj:
            return ['feed_url', 'expire_seconds', 'remove_items']
        return ['feed_url', 'expire_seconds', 'remove_items', 'group_by', 'order_by', 'reverse_order']

    def queryset(self, request):
        return super(CollectionAdmin, self).queryset(request)

    def response_change(self, request, obj):
        if obj:
            obj.perform_query(apply_options=True)
            obj.save()
        return super(FeedCollectionAdmin, self).response_change(request, obj)

    def add_view(self, *args, **kwargs):
        self.inline_instances = []
        return super(FeedCollectionAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inline_instances = []
        for inline_class in self.change_form_inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        return super(FeedCollectionAdmin, self).change_view(*args, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(FeedCollectionAdmin, self).get_form(request, obj, **kwargs)
        default_fields = self.get_default_fields(obj, request)
        if default_fields:
            default_fields += [('content_type_name', 'content_type_name')]
            default_fields.sort()
        for i in ('group_by', 'order_by', 'title_field', 'detailed_link', 'external_link'):
            if i in form.base_fields:
                form.base_fields[i].widget = forms.Select(choices=default_fields)
        return form

    def response_add(self, request, obj, post_url_continue='../%s/'):
        if obj:
            obj.perform_query(apply_options=True, force_update=True)
            obj.save()
        return super(FeedCollectionAdmin, self).response_add(request, obj, post_url_continue)


class FeedCollectionRelatedModelAdmin(SectionContentAdmin, FeedCollectionAdmin):
    tool_name = 'feed_collections'
    tool_label = _('feed collections')


def register_related(site):
    site.register_related(Collection, CollectionRelatedModelAdmin, related_to=BaseSection)
    site.register_related(FeedCollection, FeedCollectionRelatedModelAdmin, related_to=BaseSection)
    site.register_related(CollectionDisplayField, CollectionDisplayFieldAdmin, related_to=Collection)
    site.register_related(CollectionDisplayField, FeedItemDisplayFieldAdmin, related_to=FeedCollection)
    site.register_related(FeedItem, FeedItemAdmin, related_to=FeedCollection)


def register(site):
    site.register(Collection, CollectionAdmin)
    site.register(FeedCollection, FeedCollectionAdmin)
    register_related(site)
