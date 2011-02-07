# -*- coding: utf-8 -*-
from django import template
from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.conf import settings
from django.utils.importlib import import_module
from inplaceeditform.adaptors import ADAPTOR_INPLACEEDIT as DEFAULT_ADAPTOR_INPLACEEDIT

has_transmeta = False
DEFAULT_VALUE = ''
try:
    import transmeta
    has_transmeta = True
except ImportError:
    pass


def get_dict_from_obj(obj):
    obj_dict = obj.__dict__
    obj_dict_result = obj_dict.copy()
    for key, value in obj_dict.items():
        if '_id' in key:
            key2 = key.replace('_id', '')
            obj_dict_result[key2] = obj_dict_result[key]
            del obj_dict_result[key]

    manytomany_list = obj._meta.many_to_many
    for manytomany in manytomany_list:
        ids = [obj_rel.id for obj_rel in manytomany.value_from_object(obj)]
        if ids:
            obj_dict_result[manytomany.name] = ids
    return obj_dict_result


def apply_filters(value, filters, load_tags=None):
    if filters:
        filters_str = '|%s' % '|'.join(filters)
        load_tags = load_tags or []
        if load_tags:
            load_tags = "{%% load %s %%}" % ' '.join(load_tags)
        value = template.Template("""%s{{ value%s }}""" % (load_tags, filters_str)).render(template.Context({'value': value}))
    return value


def get_adaptor_class(adaptor=None, obj=None, field_name=None):
    if not adaptor:
        try:
            field = obj._meta.get_field_by_name(field_name)[0]
        except FieldDoesNotExist:
            if has_transmeta:
                field = obj._meta.get_field_by_name(transmeta.get_real_fieldname(field_name))[0]
        if isinstance(field, models.CharField):
            adaptor = 'text'
            if getattr(field, 'choices', None):
                adaptor = 'choices'
        elif isinstance(field, models.TextField):
            adaptor = 'textarea'
        elif isinstance(field, models.DateTimeField):
            adaptor = 'datetime'
        elif isinstance(field, models.DateField):
            adaptor = 'date'
        elif isinstance(field, ForeignKey):
            adaptor = 'fk'
        elif isinstance(field, ManyToManyField):
            adaptor = 'm2mcomma'
    from inplaceeditform.fields import BaseAdaptorField
    path_adaptor = adaptor and ((getattr(settings, 'ADAPTOR_INPLACEEDIT', None) and
                                 settings.ADAPTOR_INPLACEEDIT.get(adaptor, None)) or
                                 (DEFAULT_ADAPTOR_INPLACEEDIT.get(adaptor, None)))
    if not path_adaptor:
        return BaseAdaptorField
    path_module, class_adaptor = ('.'.join(path_adaptor.split('.')[:-1]), path_adaptor.split('.')[-1])
    return getattr(import_module(path_module), class_adaptor)
