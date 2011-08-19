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
from django.conf import settings


register = template.Library()


def document_section_media(context):
    tinymce_extra_media = {}
    extra_css, extra_js = settings.TINYMCE_EXTRA_MEDIA['css'], settings.TINYMCE_EXTRA_MEDIA['js']
    if extra_css:
        tinymce_extra_media['css'] = ','.join(['%s%s' % (settings.MEDIA_URL, css) for css in extra_css])
    if extra_js:
        tinymce_extra_media['js'] = ','.join(['%s%s' % (settings.MEDIA_URL, js) for js in extra_js])
    return {
        'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
        'tinymce_extra_media': tinymce_extra_media,
        'user': context['user'],
        'request': context['request'],
        'TINYMCE_LANG_SPELLCHECKER': getattr(settings, 'TINYMCE_LANG_SPELLCHECKER', '+English=en'),
        'TINYMCE_LANG': getattr(settings, 'TINYMCE_LANG', 'en'),

    }
register.inclusion_tag("section/document_section_media.html", takes_context=True)(document_section_media)


def insert_document_section_after(context, document, after=None):
    return {
        'document': document,
        'document_section': after,
    }
register.inclusion_tag("section/document_section_add.html", takes_context=True)(insert_document_section_after)
