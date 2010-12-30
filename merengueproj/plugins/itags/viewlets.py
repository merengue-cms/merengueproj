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

from operator import attrgetter

from django.utils.translation import ugettext_lazy as _

from merengue.viewlet.viewlets import Viewlet

from plugins.itags.models import ITag
from tagging.models import Tag, TaggedItem


class TagCloudViewlet(Viewlet):
    name = 'tagcloud'
    help_text = _('Tag cloud')
    verbose_name = _('Tag cloud block')

    @classmethod
    def get_tag_cloud(cls, request):
        from plugins.itags.config import PluginConfig
        dbparams = {'tag_table': Tag._meta.db_table,
                    'tag_id_field': Tag._meta.pk.name,
                    'item_table': TaggedItem._meta.db_table,
                    'item_id_field': 'tag_id'}
        taglist = Tag.objects.extra(select={
            'item_count': '''SELECT COUNT(*) FROM %(item_table)s
             WHERE %(tag_table)s.%(tag_id_field)s=%(item_table)s.%(item_id_field)s''' % dbparams,
            }).order_by('-item_count')

        tag_cloud = []
        for tag in taglist:
            limit = PluginConfig.get_config().get('max_tags_in_cloud', None)
            limit = limit and int(limit.value) or 20
            if len(tag_cloud) >= limit:
                break
            try:
                tag.itag.item_count = tag.item_count
                tag_cloud.append(tag.itag)
            except ITag.DoesNotExist:
                continue

        if not tag_cloud or tag_cloud[0].item_count == 0:
            return None

        max_item_count = tag_cloud[0].item_count # the first element is always the biggest
        for t in tag_cloud:
            t.count = (float(t.item_count) / max_item_count) + 1
        tag_cloud.sort(key=attrgetter('tag_name'))
        return tag_cloud

    @classmethod
    def render(cls, request):
        tag_cloud = cls.get_tag_cloud(request)
        return cls.render_viewlet(request, template_name='itags/viewlets/tagcloud.html',
                                  context={'taglist': tag_cloud})
