from transmeta import get_fallback_fieldname

from merengue.base.admin import BaseAdmin
from merengue.portal.models import PortalLink


class PortalLinkAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ('category', )
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}


def register(site):
    site.register(PortalLink, PortalLinkAdmin)
