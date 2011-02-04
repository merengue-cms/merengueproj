# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import simplejson

from inplaceeditform.commons import (get_dict_from_obj, apply_filters,
                                     get_adaptor_class)


@login_required
def save_ajax(request):
    if not request.method == 'POST':
        return HttpResponse(simplejson.dumps({'errors': 'It is not a POST request'}),
                            mimetype='application/json')
    adaptor = _get_adaptor(request.POST, request)
    value = simplejson.loads(request.POST.get('value'))
    new_data = get_dict_from_obj(adaptor.obj)
    form_class = adaptor.get_form_class()
    field_name = adaptor.field_name
    form = form_class(data=new_data, instance=adaptor.obj)
    value_edit = adaptor.get_value_editor(value)
    value_edit_with_filter = apply_filters(value_edit, adaptor.filters_to_edit)
    new_data[field_name] = value_edit_with_filter
    if form.is_valid():
        adaptor.save(value_edit_with_filter)
        return HttpResponse(simplejson.dumps({'errors': False,
                                         'value': adaptor.render_value()}),
                            mimetype='application/json')
    return HttpResponse(simplejson.dumps({'errors': form.errors}), mimetype='application/json')


@login_required
def get_field(request):
    if not request.method == 'GET':
        return HttpResponse(simplejson.dumps({'errors': 'It is not a GET request'}),
                            mimetype='application/json')
    adaptor = _get_adaptor(request.GET, request)
    field_render = adaptor.render_field()
    field_media_render = adaptor.render_media_field()
    return HttpResponse(simplejson.dumps({'field_render': field_render,
                                          'field_media_render': field_media_render}),
                                        mimetype='application/json')


def _get_adaptor(request_params, request):
    field_name = request_params.get('field_name', None)
    obj_id = request_params.get('obj_id', None)
    content_type_id = request_params.get('content_type_id', None)

    filters_to_show = simplejson.loads(request_params.get('filters_to_show', None))
    filters_to_edit = simplejson.loads(request_params.get('filters_to_edit', None))
    field_adaptor = request_params.get('field_adaptor', None)
    class_inplace = request_params.get('class_inplace', None)

    if not field_name or not obj_id or not content_type_id:
        return HttpResponse(simplejson.dumps({'errors': 'Params insufficient'}),
                            mimetype='application/json')

    contenttype = ContentType.objects.get(id=content_type_id)
    model_class = contenttype.model_class()
    obj = get_object_or_404(model_class, id=obj_id)
    class_field = get_adaptor_class(field_adaptor, obj, field_name)
    height = request_params.get('height', False)
    width = request_params.get('width', False)
    options = {'height': height, 'width': width}

    adaptor = class_field(field_name, obj, request,
                          filters_to_show, filters_to_edit,
                          class_inplace, **options)
    return adaptor
