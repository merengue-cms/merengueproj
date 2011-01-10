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

from django.shortcuts import get_object_or_404

from merengue.base.views import content_list
from plugins.itags.models import ITag
from tagging.models import TaggedItem


def tag_view(request, tag_name):
    model = request.GET.get('model', None)
    itag = get_object_or_404(ITag, name=tag_name)
    queryset = TaggedItem.objects.filter(tag=itag.tag_ptr)
    if model:
        queryset = queryset.filter(content_type__model=model)
    return content_list(request, queryset,
                        template_name='itags/itag_view.html',
                        extra_context={'tag': itag},
                       )
