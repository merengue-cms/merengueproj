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

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse

from plugins.tmtemplates.models import TMTemplate


def tmtemplate_list(request):
    templates = TMTemplate.objects.all()
    return render_to_response('tmtemplates/template_list.js', {'templates': templates})


def tmtemplate_view(request, tmtemplate_id):
    template = get_object_or_404(TMTemplate, id=tmtemplate_id)
    return HttpResponse(template.content)
