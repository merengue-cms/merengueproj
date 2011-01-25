from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from transmeta import get_real_fieldname

from merengue.base.models import BaseContent
from merengue.collection.models import (Collection, IncludeCollectionFilter,
                                        CollectionDisplayField,
                                        CollectionDisplayFieldFilter,
                                        FeedCollection)


def get_common_fields_for_cts(content_types):
    result = set()
    extrange = False
    for ct in content_types:
        model = ct.model_class()
        if not issubclass(model, BaseContent):
            extrange = True
        fields = set(model._meta.get_all_field_names())
        if not result:
            result = fields
        else:
            result = result.intersection(fields)
    if not extrange:
        result = result.intersection(set(BaseContent._meta.get_all_field_names()))
    return result


def get_common_fields_no_language_from_fields(fields):
    result = set()
    languages_sufixes = ['_%s' % i[0] for i in settings.LANGUAGES]
    for field in fields:
        if field[-3:] in languages_sufixes:
            field = field[:-3]
        result.add(field)
    return result


def get_common_fields_no_language(collection):
    fields = get_common_fields(collection)
    return get_common_fields_no_language_from_fields(fields)


def get_common_feed_fields(collection):
    items = collection.feeditem_set.all()
    if not items.count():
        return []
    first = items[0].get_real_item()
    return first.keys()


def get_common_fields(collection):
    if isinstance(collection, FeedCollection):
        return get_common_feed_fields(collection)
    return get_common_fields_for_cts(collection.content_types.all())


def create_normalize_collection(slug, name, model, create_display_field=True,
                                create_filter_field=True):
    ct = ContentType.objects.get_for_model(model)
    sp = transaction.savepoint()
    collection, created = Collection.objects.get_or_create(slug=slug)
    transaction.savepoint_commit(sp)

    if created:
        collection.status = 'published'
        collection.no_changeable_fields = [
            'slug', get_real_fieldname('name', settings.LANGUAGE_CODE)]
        collection.no_deletable = True
        setattr(collection,
                get_real_fieldname('name', settings.LANGUAGE_CODE),
                name)
        collection.save()

        if create_filter_field:
            IncludeCollectionFilter.objects.create(
                collection=collection, filter_field='status',
                filter_operator='exact', filter_value='published')
            if create_display_field:
                dfield = CollectionDisplayField.objects.create(
                    field_name='description', safe=True,
                    show_label=False, collection=collection)
                CollectionDisplayFieldFilter.objects.create(
                    display_field=dfield,
                    filter_module='django.template.defaultfilters.truncatewords_html',
                    filter_params='15')
            collection.content_types.add(ct)
