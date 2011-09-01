from django.conf import settings
from django.template.loader import render_to_string
from django.template import RequestContext, defaultfilters
from django.utils.translation import ugettext_lazy as _

from copy import deepcopy
from django.db import connection
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


def table_exists(table):
    return table in connection.introspection.get_table_list(connection.cursor())


def get_render_http_error(request, http_error):
    template = settings.HTTP_STATUS_CODE_TEMPLATES.get(http_error, None)
    context = {'template_base': 'viewlet_error.html', 'is_admin': False}
    return render_to_string(template, context,
                                      context_instance=RequestContext(request))


def get_login_url():
    from merengue.pluggable.utils import get_plugin
    core_config = get_plugin('core').get_config()
    login_url_conf = core_config.get('login_url', None)
    if not login_url_conf:
        return settings.LOGIN_URL
    else:
        return login_url_conf.get_value() or settings.LOGIN_URL


def get_unique_slug(value, queryset, slug_field='slug'):
    """ Get the first empty slug in the queryset """
    slug = original_slug = defaultfilters.slugify(value)
    n = 2
    filters = {slug_field: slug}
    while queryset.filter(**filters).exists():
        slug = original_slug + u'-%s' % n
        filters[slug_field] = slug
        n += 1
    return slug


def get_translate_status_list():
    return ((status_code, _(status_text)) for status_code, status_text in settings.STATUS_LIST)
