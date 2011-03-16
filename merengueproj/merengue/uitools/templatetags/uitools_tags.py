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

from django import template

from classytags.core import Tag, Options
from classytags.arguments import Argument

from merengue.pluggable.models import RegisteredPlugin


register = template.Library()


class RenderPanel(Tag):
    name = 'render_panel'
    options = Options(
        Argument('panel'),
    )

    def render_tag(self, context, panel):
        if panel.show(context):
            return '<li>%s</li>' % panel.render(context)
        return ''
register.tag(RenderPanel)


@register.inclusion_tag('uitools/toolbar.html', takes_context=True)
def render_toolbar(context):
    active_plugins = RegisteredPlugin.objects.actives().get_items()
    panels = []
    for plugin in active_plugins:
        panels.extend(plugin.get_toolbar_panels_items())
    return {
        'MEDIA_URL': context['MEDIA_URL'],
        'request': context['request'],
        'user': context['user'],
        'panels': panels,
        'content': context.get('content', None),
    }
