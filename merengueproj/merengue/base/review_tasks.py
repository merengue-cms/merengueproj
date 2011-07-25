from django.utils.translation import ugettext as _

from merengue.review import create_review_task
from merengue.review.utils import get_reviewers


def review_to_pending_status(obj, original_status):
    if not obj.last_editor:
        return

    create_review_task(
        owner=obj.last_editor,
        title=_(u'%s set to pending state') % obj,
        url=obj.get_admin_absolute_url(),
        task_object=obj,
        users=get_reviewers(obj),
    )
