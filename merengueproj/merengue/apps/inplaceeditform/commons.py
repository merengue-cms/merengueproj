# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.forms.models import modelform_factory, ModelMultipleChoiceField
from django.forms.fields import MultipleChoiceField
from django.contrib.contenttypes.models import ContentType

has_transmeta = False
DEFAULT_VALUE = ''
try:
    from transmeta import TransMeta
    has_transmeta = True
except ImportError:
    pass


def change_foreing_key(obj):
    obj_dict = obj.__dict__
    obj_dict_result = obj_dict.copy()
    for key, value in obj_dict.items():
        if '_id' in key:
            key2 = key.replace('_id', '')
            obj_dict_result[key2] = obj_dict_result[key]
            del obj_dict_result[key]

    manytomany_list = obj._meta.many_to_many
    for manytomany in manytomany_list:
        obj_dict_result[manytomany.name] = [obj_rel.id for obj_rel in manytomany.value_from_object(obj)]
    return obj_dict_result


def apply_filters(value, filters):
    if filters:
        filters_str = '|%s' % '|'.join(filters)
        value = template.Template("""{{ value%s }}""" % filters_str).render(template.Context({'value': value}))
    return value


def get_form_class(form_str=None, content_type_id=None):
    if form_str:
        path_split = form_str.split('.')
        return getattr(__import__('.'.join(path_split[:len(path_split)-1]), {}, {}, [path_split[len(path_split)-1]]), path_split[(len(path_split)-1)])
    contenttype = ContentType.objects.get(id=content_type_id)
    return modelform_factory(contenttype.model_class())


def special_procesing(field_obj, value):
    if isinstance(field_obj.field, MultipleChoiceField) or isinstance(field_obj.field, ModelMultipleChoiceField):
        value = value.all()
        value =[v.__unicode__() for v in value]
        value = ','.join(value)

    if field_obj.form._meta.model._meta.get_field(field_obj.name) and field_obj.form._meta.model._meta.get_field(field_obj.name).choices:
        choices_dict = dict(field_obj.form._meta.model._meta.get_field(field_obj.name).choices)
        value = choices_dict[value]

    return value


def has_translation(field_obj, obj, current_language):
    if has_transmeta and getattr(obj._meta, 'translatable_fields', None):
        name_field = field_obj.name.split('_')
        if len(name_field) > 1 and name_field[0] in obj._meta.translatable_fields and \
           getattr(obj, field_obj.name) and not getattr(obj, field_obj.name) == DEFAULT_VALUE:
            return True
    return False


def transmeta_procesing(field_obj, value, obj, current_language):
    if has_transmeta and not has_translation(field_obj, obj, current_language):
        field_name_generic = field_obj.name.split('_')
        if len(field_name_generic) > 1 and field_name_generic[-1] in [lcode for lcode, ldescription in settings.LANGUAGES]:
            value = getattr(obj, field_name_generic[0])
    return value
