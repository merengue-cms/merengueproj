from merengue.base.admin import BaseAdmin
from plugins.voting.models import Vote


class VoteAdmin(BaseAdmin):
    pass


def register(site):
    """ Merengue admin registration callback """
    site.register(Vote, VoteAdmin)
