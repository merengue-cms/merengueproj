# -*- coding: utf-8 -*-

from django.conf import settings

from themes.models import Theme


def media(request):
    try:
        active_theme = Theme.objects.active()
        return {
            'THEME_MEDIA_URL': '%sthemes/%s/' % (settings.MEDIA_URL, active_theme.directory_name),
        }
    except Theme.DoesNotExist:
        return {}
