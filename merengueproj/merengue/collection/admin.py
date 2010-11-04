from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from transmeta import get_real_fieldname_in_each_language

from merengue.base.admin import BaseContentAdmin

from merengue.base.models import BaseContent
from merengue.collection.models import (Collection, IncludeCollectionFilter,
                                        ExcludeCollectionFilter,
                                        CollectionDisplayField)


class CollectionFilterInline(admin.TabularInline):
    pass


class ExcludeCollectionFilterInline(CollectionFilterInline):
    model = ExcludeCollectionFilter


class IncludeCollectionFilterInline(CollectionFilterInline):
    model = IncludeCollectionFilter


class CollectionDisplayFieldInline(admin.TabularInline):
    model = CollectionDisplayField


class CollectionAdmin(BaseContentAdmin):
    fieldsets = (
        (_('Collection Basic Information'),
            {'fields': get_real_fieldname_in_each_language('name') +\
                       ['slug', ] +\
                       get_real_fieldname_in_each_language('description') +\
                       ['status', 'tags', 'meta_desc', 'commentable', 'owners']},
            ),
        (_('Collection Configuration'),
            {'fields': ('content_types', 'group_by', 'order_by', 'reverse_order', )},
            ),
        )
    filter_horizontal = BaseContentAdmin.filter_horizontal + ('content_types', )
    inlines = [IncludeCollectionFilterInline, ExcludeCollectionFilterInline,
               CollectionDisplayFieldInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super(CollectionAdmin, self).get_form(request, obj, **kwargs)
        if 'content_types' in form.base_fields:
            main_models = BaseContent.__subclasses__()
            types_id = []
            for m in main_models:
                types_id.append(ContentType.objects.get_for_model(m).id)
            form.base_fields['content_types'].queryset = form.base_fields['content_types'].queryset.filter(id__in=types_id)
        return form


def register(site):
    site.register(Collection, CollectionAdmin)
