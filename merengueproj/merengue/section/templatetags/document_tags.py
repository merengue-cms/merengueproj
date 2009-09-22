from django import template
from django.conf import settings


register = template.Library()


def document_section_media(context):
    return {'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
           }
register.inclusion_tag("section/document_section_media.html", takes_context=True)(document_section_media)


def insert_document_section_after(context, document, after=None):
    return {'document': document,
            'document_section': after,
            }
register.inclusion_tag("section/document_section_add.html", takes_context=True)(insert_document_section_after)
