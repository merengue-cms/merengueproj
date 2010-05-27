# -*- coding: utf-8 -*-
from merengue.theming.models import Theme


def media(request):
    try:
        active_theme = Theme.objects.active()
        return {
            'theme': active_theme.name,
            'THEME_MEDIA_URL': active_theme.get_theme_media_url(),
        }
    except Theme.DoesNotExist:
        return {}
