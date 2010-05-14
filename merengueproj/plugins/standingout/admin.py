from merengue.base.admin import BaseAdmin

from plugins.standingout.models import StandingOut


class StandingOutAdmin(BaseAdmin):
    pass


def register(site):
    """ Merengue admin registration callback """
    site.register(StandingOut, StandingOutAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(StandingOut)
