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

from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import RelatedModelAdmin
from merengue.base.models import BaseContent
from merengue.block.models import RegisteredBlock, BlockContentRelation
from merengue.block.forms import BaseContentRelatedBlockForm
from merengue.registry.admin import RegisteredItemAdmin


class RegisteredBlockAdmin(RegisteredItemAdmin):
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name', )
    list_display = RegisteredItemAdmin.list_display + ('placed_at', )
    list_filter = ('placed_at', )
    ordering = ('order', )

    fieldsets = (
        ('', {'fields': ('name', 'module', 'class_name', )}),
        (_('Status'),
            {'fields': ('placed_at', 'active', 'shown_in_urls', 'hidden_in_urls', 'order', 'config')}
        ))

    def has_add_permission(self, request):
        return False


class BaseContentRelatedBlockAdmin(RelatedModelAdmin):
    tool_name = 'block_content_related'
    tool_label = _('block content related')
    related_field = 'content'
    form = BaseContentRelatedBlockForm


def register(site):
    site.register(RegisteredBlock, RegisteredBlockAdmin)
    site.register_related(BlockContentRelation, BaseContentRelatedBlockAdmin,
                          related_to=BaseContent)
