from copy import deepcopy
from django.conf import settings
from south.db import db
from transmeta import (get_real_fieldname_in_each_language, get_field_language,
                       fallback_language)


def south_trans_data(orm, trans_data):
    fields = []
    for model, trans_fields in trans_data.items():
        for field_name in trans_fields:
            for real_field in get_real_fieldname_in_each_language(field_name):
                fields.append((real_field, orm['%s:%s' % (model, real_field)]))
    return tuple(fields)


def add_south_trans_fields(frozen_models, trans_data):
    for model, field_data in trans_data.items():
        for field_name, field_desc in field_data.items():
            for real_field in get_real_fieldname_in_each_language(field_name):
                field_lang = get_field_language(real_field)
                real_field_desc = deepcopy(field_desc)
                if field_lang != fallback_language():
                    real_field_desc[2].update({'null': 'True', 'blank': 'True'})
                frozen_models[model][real_field] = real_field_desc


def add_south_trans_column(table, model_name, field_name, orm):
    for real_field in get_real_fieldname_in_each_language(field_name):
        db.add_column(table, real_field, orm['%s:%s' % (model_name, real_field)])


def delete_south_trans_column(table, field_name):
    for real_field in get_real_fieldname_in_each_language(field_name):
        db.delete_column(table, real_field)