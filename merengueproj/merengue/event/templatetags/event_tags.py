from django import template
from django.db.models import Q

from event.models import Event
from merengue.multimedia.models import Photo

from datetime import datetime

register = template.Library()


@register.inclusion_tag('event/event_address_info.html', takes_context=True)
def occurrence_address_info(context, occurrence):
    return {'occurrence': occurrence,
            'location': occurrence.get_location(),
            'request': context.get('request')}


@register.inclusion_tag('event/event_contact_info.html', takes_context=True)
def occurrence_contact_info(context, occurrence):
    contact_info = None
    basecontent_contact_info = None
    if occurrence is not None:
        if occurrence.contact_info is not None:
            contact_info = occurrence.contact_info
        if occurrence.basecontent_location is not None and occurrence.basecontent_location.contact_info:
            basecontent_contact_info = occurrence.basecontent_location.contact_info
    return {'has_contact_info': contact_info or basecontent_contact_info,
            'contact_info': contact_info,
            'basecontent_contact_info': basecontent_contact_info,
            'request': context.get('request')}


@register.inclusion_tag('event/event_contact_info_contain.html', takes_context=True)
def event_contact_info_contain(context, contact):
    return {'contact': contact,
            'request': context.get('request')}


@register.inclusion_tag('event/event_categories.html', takes_context=True)
def event_categories(context, event):
    return {'event': event, 'request': context.get('request')}


@register.inclusion_tag('event/range_dates.html', takes_context=True)
def range_dates(context, start, end):
    if end == start:
        end = None
    return {'start': start,
            'end': end,
            'request': context.get('request')}


@register.inclusion_tag('event/range_dates_as_tag.html', takes_context=True)
def range_dates_as_tag(context, start, end, tag='span', classdef=None):
    if end == start:
        end = None
    return {'start': start,
            'end': end,
            'classdef': classdef,
            'tag': tag,
            'request': context.get('request')}


@register.inclusion_tag('event/related_events.html', takes_context=True)
def related_events(context, event):
    active_event_filter = {'status': 'published',
                           'cached_max_end__gte': datetime.now(),
                           }
    children = event.event_set.filter(**active_event_filter)
    if children == []:
        children = event.event_set.filter(status='published')
    parent = event.parent
    if parent and parent.status == 'published':
        brothers = event.parent.event_set.filter(**active_event_filter)
        if brothers == []:
            brothers = event.parent.event_set.filter(status='published')
    else:
        parent = None
        brothers = []

    return {'event': event,
            'children': children,
            'parent': parent,
            'brothers': brothers and None,
            'request': context.get('request')}


@register.inclusion_tag('base/media_slide.html', takes_context=True)
def event_media_slide(context, event):
    content_images = list(event.multimedia.photos().order_by('multimediarelation__order'))
    children_event = event.event_set.all().values('pk').query
    content_images += list(Photo.objects.filter(basecontent__in=children_event).order_by('multimediarelation__order'))
    content_videos = event.multimedia.videos().order_by('multimediarelation__order')
    content_image3d = event.multimedia.images3d().order_by('multimediarelation__order')
    content_panoramicview = event.multimedia.panoramic_views().order_by('multimediarelation__order')
    return {'content': event,
            'content_images': content_images,
            'content_videos': content_videos,
            'content_image3d': content_image3d,
            'content_panoramicview': content_panoramicview,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


@register.inclusion_tag('event/highlight_events.html', takes_context=True)
def highlight_events(context, section=None, event_number=3):
    filter_section = Q()
    if section:
        filter_section = Q(categories__sections__in=[section]) | Q(categories__groups__sections__in=[section])

    highlight_events = Event.objects.published().filter(is_highlight=True).filter(filter_section).distinct()
    highlight_events_count = highlight_events.count()

    if highlight_events_count < event_number:
        events = Event.objects.published().filter(filter_section).distinct()
        highlight_events = highlight_events | events
    highlight_events = highlight_events.order_by('-is_highlight', 'cached_min_start')[:event_number]
    return {'highlight_events': highlight_events}
