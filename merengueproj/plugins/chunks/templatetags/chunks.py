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

from transmeta import get_fallback_fieldname

register = template.Library()

Chunk = models.get_model('chunks', 'chunk')
CACHE_PREFIX = "chunk_"


def inplace_chunk(context, key, default_text='Text created automatically', mode="textarea"):
    """
    Render a chunk, with the possibility to edit it inplace.
    ``mode`` is "textarea" or "text". "textarea" will use a HTML visual editor.
    """
    try:
        chunk = Chunk.objects.get(key=key)
    except Chunk.DoesNotExist:
        content_field = get_fallback_fieldname('content')
        chunk = Chunk(key=key)
        setattr(chunk, content_field, default_text)
        chunk.save()
    return {'object': chunk,
            'MEDIA_URL': context.get('MEDIA_URL', ''),
            'request': context['request'],
            'mode': mode,
           }
register.inclusion_tag("chunks/chunk.html", takes_context=True)(inplace_chunk)
