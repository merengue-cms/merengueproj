from transmeta import get_fallback_fieldname

from merengue.base.admin import BaseAdmin
from plugins.highlight.models import Highlight


class HighlightAdmin(BaseAdmin):
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}
    html_fields = ('description', )


def register(site):
    """ Merengue admin registration callback """
    site.register(Highlight, HighlightAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Highlight)
