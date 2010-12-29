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

from django import template
from django.db import models
from django.core.cache import cache
from django.conf import settings


register = template.Library()

Chunk = models.get_model('chunks', 'chunk')
CACHE_PREFIX = "chunk_"


def inplace_chunk(context, key, mode='simple', height=100, cache_time=0):
    try:
        cache_key = CACHE_PREFIX + key
        c = cache.get(cache_key)
        if c is None:
            c = Chunk.objects.get(key=key)
            cache.set(cache_key, c, int(cache_time))
    except Chunk.DoesNotExist:
        content = ''
    return {'object': c,
            'form': 'plugins.chunks.forms.forms.ChunkForm',
            'MEDIA_URL': context.get('MEDIA_URL', ''),
            'user': getattr(context['request'], 'user', None),
           }
register.inclusion_tag("chunks/chunk.html", takes_context=True)(inplace_chunk)


def inplace_media_chunk(context):
    return {
            'request': context['request'],
            'user': context['request'].user,
            'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
    }
register.inclusion_tag("chunks/chunk_media.html", takes_context=True)(inplace_media_chunk)
