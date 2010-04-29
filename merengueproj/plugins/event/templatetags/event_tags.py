from django import template

register = template.Library()


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
