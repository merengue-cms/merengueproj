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

from merengue.base.models import BaseContent
from plugins.event.models import Event
from merengue.places.models import BaseCity, Province, TouristZone

register = template.Library()


@register.inclusion_tag('event/portlet_content_active_events.html', takes_context=True)
def portlet_content_active_events(context, content, limit=7):
    """
        Show a portlet with active events which are located in content
    """
    try:
        if isinstance(content, BaseCity):
            filter = {'location__cities': content}
        elif isinstance(content, Province):
            filter = {'location__cities__province': content}
        elif isinstance(content, TouristZone):
            filter = {'location__cities__in': content.cities.published()}
        elif isinstance(content, BaseContent):
            filter = {'occurrence_event__basecontent_location': content}
        related_events = Event.objects.actives().filter(**filter).order_by('start')

        return {'content': content,
                'events': related_events[:limit],
                'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
                'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
                'request': context.get('request', None)}
    except:
        pass
