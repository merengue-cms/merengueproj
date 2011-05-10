from django.template import Library

register = Library()


@register.filter
def verbose_name_plural(obj):
    """
    Returns pluralmeta class name
    """
    return obj._meta.verbose_name_plural
