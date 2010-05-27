from django.conf import settings
from django.template import Library

from merengue.theming.models import Theme

register = Library()


@register.filter
def replace_variables(value, arg=None):
    value = value.replace('$media_url', settings.MEDIA_URL)
    try:
        active_theme = Theme.objects.active()
        value = value.replace('$theme_url', active_theme.get_theme_media_url())
    except Theme.DoesNotExist:
        pass
    return value
