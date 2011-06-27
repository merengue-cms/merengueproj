from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.fields import FieldDoesNotExist
from django.template import loader

from transmeta import get_real_fieldname

from merengue.base.models import BaseContent
from merengue.collection.models import (Collection, IncludeCollectionFilter,
                                        CollectionDisplayField,
                                        CollectionDisplayFieldFilter,
                                        FeedCollection)


from stdimage import StdImageField
from django.db.models import ImageField, ManyToManyField
from tagging.fields import TagField

NOT_ORDERING_FIELD_TYPES = [StdImageField,
                            ImageField,
                            ManyToManyField,
                            TagField]

NOT_ORDERING_FIELD_NAMES = ['adquire_global_permissions',
                            'cached_plain_text',
                            'has_related_blocks',
                            'meta_desc',
                            'multimediarelation',
                            'no_changeable',
                            'no_changeable_fields',
                            'no_deletable',
                            'objectpermission',
                            'objectpermissioninheritanceblock',
                            'principalrolerelation', ]


def get_common_fields_for_cts(content_types):
    result = set()
    extrange = len(content_types) == 1
    for ct in content_types:
        model = ct.model_class()
        if not model:
            continue
        if not issubclass(model, BaseContent):
            extrange = True
        fields = set(model._meta.get_all_field_names())

        # remove all fields that are not suitable for ordering
        not_ordering = set()
        for f in fields:
            if f in NOT_ORDERING_FIELD_NAMES:
                not_ordering.add(f)
                continue
            try:
                field = model._meta.get_field_by_name(f)[0]
                for fieldtype in NOT_ORDERING_FIELD_TYPES:
                    if isinstance(field, fieldtype):
                        not_ordering.add(f)
                        break
            except FieldDoesNotExist:
                not_ordering.add(f)
        fields = fields.difference(not_ordering)

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


def get_common_field_translated_name(collection, field):
    """
    Return the translation field if it exists for all collection models,
    or the original field otherwise.
    """
    model = collection.get_first_parents_of_content_types()
    if not model:
        return field
    import transmeta
    translatables = transmeta.get_all_translatable_fields(model)

    common_fields = get_common_fields(collection)

    if field in translatables:
        real_field = get_real_fieldname(field)
        if real_field in common_fields:
            return real_field
    return field


def create_normalize_collection(slug, name, model, create_display_field=True,
                                create_filter_field=True):
    ct = ContentType.objects.get_for_model(model)
    sp = transaction.savepoint()
    collection, created = Collection.objects.get_or_create(slug=slug)
    transaction.savepoint_commit(sp)

    if created:
        collection.status = 'published'
        collection.no_deletable = True
        setattr(collection,
                get_real_fieldname('name', settings.LANGUAGE_CODE),
                name)
        collection.no_changeable_fields = [
            'slug', 'name', get_real_fieldname('name', settings.LANGUAGE_CODE)]
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

    return collection


def get_render_item_template(model_collection):
    template_list = []
    if model_collection:
        template_list += ['%s/collection_item.html' % m._meta.module_name \
                          for m in model_collection.mro() \
                          if getattr(m, '_meta', None) and not m._meta.abstract]
    return loader.select_template(template_list + ['collection/collection_item.html'])
