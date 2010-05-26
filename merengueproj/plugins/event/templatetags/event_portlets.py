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
