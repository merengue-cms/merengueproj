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
    }
register.inclusion_tag("section/document_section_media.html", takes_context=True)(document_section_media)


def insert_document_section_after(context, document, after=None):
    return {
        'document': document,
        'document_section': after,
    }
register.inclusion_tag("section/document_section_add.html", takes_context=True)(insert_document_section_after)
