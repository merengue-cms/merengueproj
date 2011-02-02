# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site


def google_api_key(request):
    """
    Adds Google API key-related context variables to the context.
    """
    if hasattr(settings, 'GOOGLE_MAPS_API_KEY'):
        return {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}
    return {}


def site(request):
    current_site = Site.objects.get_current()
    all_sites = {}
    for site in Site.objects.all():
        all_sites[site.id] = dict(site_domain=site.domain, site_name=site.name)
    return {
        'site_domain': current_site.domain,
        'site_name': current_site.name,
        'sites': all_sites,
    }


def expire_time_cached(request):
    """
    Adds expire time of cached context variables to the context.
    """
    if hasattr(settings, 'CACHE_MIDDLEWARE_SECONDS'):
        return {'EXPIRE_TIME': settings.CACHE_MIDDLEWARE_SECONDS}
    return {}


def coming_from_buildbot(request):
    context = {'coming_from_buildbot': False}
    if hasattr(settings, 'BUILDBOT_IP'):
        if request.META.get('REMOTE_ADDR') == settings.BUILDBOT_IP:
            context['coming_from_buildbot'] = True
    return context


def merengue_urls_prefix(request):
    return {'MERENGUE_URLS_PREFIX': settings.MERENGUE_URLS_PREFIX}


def is_homepage(request):
    return {'is_homepage': request.path == '/'}


def all_context(request):
    """
    Add all template context
    """
    context = dict()
    context.update(google_api_key(request))
    context.update(site(request))
    context.update(expire_time_cached(request))
    context.update(coming_from_buildbot(request))
    context.update(merengue_urls_prefix(request))
    context.update(is_homepage(request))
    # add here more context dict to the request
    return context
