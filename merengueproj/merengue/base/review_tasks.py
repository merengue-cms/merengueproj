from django.contrib.auth.models import User

from merengue.review import create_review_task


def review_to_pending_status(obj, original_status):
    from merengue.perms import utils as perms_api

    if not obj.last_editor:
        return

    create_review_task(
        owner=obj.last_editor,
        title=u'%s set to pending state' % obj,
        url=obj.get_admin_absolute_url(),
        task_object=obj,
        users=[i for i in User.objects.all() if perms_api.has_permission(obj, i, 'can_published')]
    )
