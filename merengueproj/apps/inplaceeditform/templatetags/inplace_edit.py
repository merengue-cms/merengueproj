# -*- coding: utf-8 -*-

from django.template import Library, Variable
from django.conf import settings
from django.utils import simplejson
from django.utils.translation import ugettext_lazy
from django.utils.translation import get_language
from django.contrib.contenttypes.models import ContentType

from inplaceeditform.commons import (get_form_class, apply_filters,
                                     special_procesing, 
                                     has_translation)

register = Library()

def inplace_media(context):
    return context.update({
            'user': context['request'].user,
            'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
    })
register.inclusion_tag("inplace_media.html", takes_context=True)(inplace_media)


def inplace_edit(context, obj, expression, form='', expression2=None):
    content_type_id = ContentType.objects.get_for_model(obj.__class__).id
    form_class = get_form_class(form, content_type_id)
    prefix = '%s_%s'%(content_type_id, obj.id)
    form_obj = form_class(instance=obj, prefix=prefix)
    tokens = expression.split('|')
    field, filters = tokens[0], tokens[1:]
    current_language = get_language()
    field_lang = None
    if field in form_obj.fields:
        field_obj = form_obj[field]
    else:
        field_lang = "%s_%s" %(field, current_language)
        field_obj = form_obj[field_lang]


    value = getattr(obj, field, '-----')
    value = special_procesing(field_obj, value)


    value = apply_filters(value, filters)

    empty_value = (isinstance(value, str) and value.strip() == u'' or not value)

    if field_lang and not has_translation(field_obj, obj, current_language):
        missing_msg = u'<h3 class="missing-translation">%s</h3>' % ugettext_lazy('Translation missing')
        form_obj.initial[field_obj.name] = missing_msg 
        old_value = form_obj.initial[field_obj.name]
        if old_value:
            form_obj.initial[field_obj.name] = old_value 


    if expression2:
        tokens = expression2.split('|')
        field2, filters2 = tokens[0], tokens[1:]
        value2 = Variable(field2).resolve(context)
        value2 = apply_filters(value2, filters2)
    else:
        value2 = None

    return {
            'obj': obj,
            'field': field_obj,
            'content_type_id': content_type_id,
            'form': form,
            'form_obj': form_obj,
            'value':  value,
            'value2':  value2,
            'empty_value': empty_value,
            'filters': simplejson.dumps(filters),
            'MEDIA_URL': context.get('MEDIA_URL',''),
            'user': context.get('user',None),
    }
register.inclusion_tag("inplace_edit.html", takes_context=True)(inplace_edit)

