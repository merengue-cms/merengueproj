from django.conf import settings

from merengue.base.models import BaseContent


def get_common_fields_for_cts(content_types):
    result = set()
    extrange = False
    for ct in content_types:
        model = ct.model_class()
        if not issubclass(model, BaseContent):
            extrange=True
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


def get_common_fields(collection):
    return get_common_fields_for_cts(collection.content_types.all())
