from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from base.decorators import content_public_required
from base.views import search_results
from searchform.utils import search_button_submitted
from section.views import section_view

from rating.models import Vote

from event.models import Event, Occurrence
from event.forms import EventQuickSearchForm, EventAdvancedSearchForm


def event_index(request):
    context = _get_event_search_context(EventQuickSearchForm)
    return section_view(request, 'eventos', context, 'event/event_index.html')


@content_public_required(slug_field='event_slug', model=Event)
def event_view(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    show_moreoccurrences = (event.occurrence_event.count() > 1)
    if event.parent and event.parent.status == 'published':
        parent=event.parent
    else:
        parent=None

    children_occurrences = Occurrence.objects.filter(event__parent__id=event.id, event__status='published')
    occurrences = event.occurrence_event.all()
    event_pois = list(children_occurrences) + list(occurrences)

    return render_to_response('event/event_view.html',
                              {'event': event,
                               'parent': parent,
                               'event_pois': event_pois,
                               'show_moreoccurrences': show_moreoccurrences},
                              context_instance=RequestContext(request))


def event_search(request):
    return HttpResponseRedirect(reverse('event_quick_search'))


def _get_event_search_context(form_class):
    return {
            'quick_search_url': reverse('event_quick_search'),
            'advanced_search_url': reverse('event_advanced_search'),
            'content': None,
            'search_form': form_class(),
            }


def _internal_event_search(request, form_class):
    if search_button_submitted(request):
        return search_results(request, form_class())
    else:
        context = _get_event_search_context(form_class)
        return render_to_response('event/search.html', context,
                                  context_instance=RequestContext(request))


def event_quick_search(request):
    return _internal_event_search(request, EventQuickSearchForm)


def event_advanced_search(request):
    return _internal_event_search(request, EventAdvancedSearchForm)


def top_events_rated(request):
    class_name = 'event'
    msg_results = "top rated events"
    events = Vote.objects.get_top(Event, limit=10)
    object_list = []
    photos = []
    for event, rating in events:
        photos += event.multimedia.photos()
        event.rating = rating
        object_list.append(event)
    return render_to_response('event/top_events.html',
                              {'object_list': object_list,
                               'photos': photos},
                              context_instance=RequestContext(request))
