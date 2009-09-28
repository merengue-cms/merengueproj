# -*- coding: utf-8 -*-

from django.conf import settings

from merengue.themes.models import Theme


def media(request):
    try:
        active_theme = Theme.objects.active()
        return {
            'theme': active_theme.name,
            'THEME_MEDIA_URL': '%sthemes/%s/' % (settings.MEDIA_URL, active_theme.directory_name),
        }
    except Theme.DoesNotExist:
        return {}
