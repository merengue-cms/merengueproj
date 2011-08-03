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

from merengue.base.models import BaseContent
from merengue.base.views import content_list
from merengue.section.models import BaseSection
from plugins.itags.models import ITag
from plugins.itags.viewlets import TagCloudViewlet
from tagging.models import TaggedItem
from merengue.viewlet.models import RegisteredViewlet


def tag_view(request, tag_name):
    model = request.GET.get('model', None)
    itag = get_object_or_404(ITag, name=tag_name)
    queryset = TaggedItem.objects.filter(tag=itag.tag_ptr)
    if model:
        queryset = queryset.filter(content_type__model=model)
    queryset = BaseContent.objects.published().filter(id__in=queryset.values_list('object_id'))
    section_id = request.GET.get('section', None)
    section = None
    if section_id:
        try:
            section = BaseSection.objects.get(id=section_id)
            queryset = queryset.filter(sections=section)
        except BaseSection.DoesNotExist:
            pass
    return content_list(request, queryset,
                        template_name='itags/itag_view.html',
                        extra_context={'tag': itag,
                                       'section': section},
                       )


def tag_list(request, tag_name=''):
    context = request.GET.get('context', None)
    reg_viewlet = RegisteredViewlet.objects.by_item_class(
            TagCloudViewlet,
        ).get()
    itags = reg_viewlet.get_registry_item().get_tag_cloud(request, context, False, False)
    #import ipdb; ipdb.set_trace();
    if itags:
        if tag_name:
            tag = tag_name
            itag = get_object_or_404(ITag, name=tag_name)
            queryset = TaggedItem.objects.filter(tag=itag.tag_ptr)
        else:
            tag = itags[0].tag_name
            queryset = TaggedItem.objects.filter(tag=itags[0].tag_ptr)
    else:
        tag = None
        queryset = TaggedItem.objects.none()
    return content_list(request, queryset,
                        template_name='itags/itags_list.html',
                        extra_context={'tag': tag,
                                       'itags': itags},
                        )
