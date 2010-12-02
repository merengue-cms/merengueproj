# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils import simplejson

from merengue.collection.utils import (get_common_fields_for_cts,
                                       get_common_fields_no_language_from_fields)


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
