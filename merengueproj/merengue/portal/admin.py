from merengue.base.admin import BaseAdmin
from merengue.portal.models import PortalLink


class PortalLinkAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ('category', )


def register(site):
    site.register(PortalLink, PortalLinkAdmin)
