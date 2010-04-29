from django.shortcuts import get_object_or_404

from merengue.base.views import content_view

from plugins.event.models import Event


def event_view(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    return content_view(request, event, 'event/event_view.html')
