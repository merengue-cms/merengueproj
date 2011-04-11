# Copyright (c) 2010 by Yaco Sistemas <precio@yaco.es>
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

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import ContentAction

from plugins.odtexport.models import OpenOfficeTemplate
from oot.views import render_writer_template


class ExportODT(ContentAction):
    name = 'exportodt'
    verbose_name = _('Export ODT')
    help_text = _('Export ODT block')

    def get_response(self, request, content):
        template_id = get_odt_template_id(content.__class__)
        object_id = content.id

        response = render_writer_template(request, template_id, object_id)
        content_disp = 'attachment;filename="%s.odt"' % content.slug
        response['Content-Disposition'] = content_disp
        return response

    def has_action(self, request, content):
        return (request.user.is_authenticated() and
                content and get_odt_template_id(content.__class__) != 0)


def get_odt_template_id(content_class):
    for parent_class in content_class.mro():
        meta = getattr(parent_class, '_meta', None)
        if not meta or meta.abstract:
            continue
        content_type = ContentType.objects.get_for_model(parent_class)
        try:
            template = OpenOfficeTemplate.objects.get(content_type=content_type)
        except OpenOfficeTemplate.DoesNotExist:
            pass
        else:
            return template.id
    return 0
