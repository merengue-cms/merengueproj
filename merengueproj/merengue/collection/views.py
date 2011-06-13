# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson

from merengue.base.decorators import login_required
from merengue.base.views import render_content
from merengue.collection.utils import (get_common_fields_for_cts,
                                       get_common_fields_no_language_from_fields,
                                       get_render_item_template)


def feeditem_view(request, content, template_name=None, extra_context=None):
    item = content.get_real_item()
    if not content.feed_collection.detailed_link and content.feed_collection.external_link:
        url = getattr(item, content.feed_collection.external_link, None)
        if url:
            return HttpResponseRedirect(url)
    full_item = content.get_full_item(content.feed_collection.detailed_link)
    extra_context = extra_context or {}
    extra_context.update({'item': full_item,
                          'collection': content.feed_collection})
    if not template_name:
        template_name = content._meta.content_view_template
    return render_content(request, content, template_name, extra_context)


def collection_view(request, content, template_name=None, extra_context=None):
    context = {}
    model_collection = content.get_first_parents_of_content_types()
    if template_name is None:
        template_name = []
        if model_collection:
            template_name += ['%s/collection_view.html' % m._meta.module_name for m in model_collection.mro() if getattr(m, '_meta', None) and not m._meta.abstract]
        template_name.append(content._meta.content_view_template)
    render_item_template = get_render_item_template(model_collection)
    context['render_item_template'] = render_item_template
    context['paginate_by'] = settings.NUM_ELEM_PER_PAGE_DEFAULT
    if extra_context:
        context.update(extra_context)
    return render_content(request, content, template_name, context)


@login_required
def get_collection_fields(request):
    result = {'success': True,
             'fields': [],
             'fields_no_lang': []}

    content_type_ids = request.GET.get('content_types', None)
    if not content_type_ids:
        return HttpResponse(simplejson.dumps(result), mimetype='text/plain')
    content_types = ContentType.objects.filter(id__in=content_type_ids.split(','))
    fields = get_common_fields_for_cts(content_types)
    all_fields = list(fields) + ['content_type_name']
    all_fields.sort()
    all_fields = [''] + all_fields
    all_fields_no_lang = list(get_common_fields_no_language_from_fields(fields)) + ['content_type_name']
    all_fields_no_lang.sort()
    all_fields_no_lang = [''] + all_fields_no_lang
    result['fields'] = all_fields
    result['fields_no_lang'] = all_fields_no_lang
    return HttpResponse(simplejson.dumps(result), mimetype='text/plain')
