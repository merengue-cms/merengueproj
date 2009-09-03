from django.contrib.comments.admin import CommentsAdmin
from plugins.feedback.models import Feedback


class FeedbackAdmin(CommentsAdmin):
    pass


def register(site):
    """ Merengue admin registration callback """
    site.register(Feedback, FeedbackAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Feedback)
