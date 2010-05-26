from merengue.base.admin import BaseAdmin
from threadedcomments.models import FreeThreadedComment


class FeedbackAdmin(BaseAdmin):
    pass


def register(site):
    """ Merengue admin registration callback """
    site.register(FreeThreadedComment, FeedbackAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(FreeThreadedComment)
