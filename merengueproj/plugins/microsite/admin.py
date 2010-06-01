from merengue.section.admin import SectionAdmin
from plugins.microsite.models import MicroSite


class MicroSiteAdmin(SectionAdmin):
    pass


def register(site):
    """ Merengue admin registration callback """
    site.register(MicroSite, MicroSiteAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(MicroSite)
