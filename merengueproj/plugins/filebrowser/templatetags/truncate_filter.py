from django import template
from django.utils.text import truncate_html_words

register = template.Library()


@register.filter("inline_truncate")
def inline_truncate(value, size):
    """Truncates a string to the given size using the dots at the middle of the string"""
    if len(value) > size and size > 3:
        start = (size - 3) / 2
        end = (size - 3) - start
        return value[0:start] + '...' + value[-end:]
    else:
        return value[0:size]


@register.inclusion_tag('portal/truncate_link.html')
def truncatewords_link(value, size, obj):
    """Truncates a string to the given size
    using the dots, and if it oversize the given length, is shows
    a Read More link"""
    content = {"value": truncate_html_words(value, size)}
    words = value.split()
    if len(words) > size:
        content["obj"] = obj
    return content
