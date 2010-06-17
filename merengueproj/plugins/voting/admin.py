from merengue.base.admin import BaseAdmin, RelatedModelAdmin
from merengue.base.models import BaseContent

from plugins.voting.models import Vote


class VoteAdmin(BaseAdmin):
    pass


class VoteRelatedModelAdmin(RelatedModelAdmin, VoteAdmin):
    related_field = 'content'
    one_to_one = True


def register(site):
    """ Merengue admin registration callback """
    site.register(Vote, VoteAdmin)
    site.register_related(Vote, VoteRelatedModelAdmin, related_to=BaseContent)
