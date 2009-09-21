from merengue.base.admin import BaseAdmin

from merengue.collab.models import (CollabComment, CollabCommentRevisorStatusType,
                                    CollabCommentUserType, CollabCommentRevisorStatus)


class CollablCommentModelAdmin(BaseAdmin):
    pass


class CollablCommentRevisorStatusTypeModelAdmin(BaseAdmin):
    pass


class CollablCommentUserTypeModelAdmin(BaseAdmin):
    pass


class CollablCommentRevisorStatusModelAdmin(BaseAdmin):
    pass


def register(site):
    site.register(CollabComment, CollablCommentModelAdmin)
    site.register(CollabCommentRevisorStatusType, CollablCommentRevisorStatusTypeModelAdmin)
    site.register(CollabCommentUserType, CollablCommentUserTypeModelAdmin)
    site.register(CollabCommentRevisorStatus, CollablCommentRevisorStatusModelAdmin)
