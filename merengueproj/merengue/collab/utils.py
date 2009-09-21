from django.contrib.contenttypes.models import ContentType

from merengue.collab.models import CollabComment


def get_comments_for_object(obj):
    ct = ContentType.objects.get_for_model(obj)
    return CollabComment.objects.filter(content_type=ct, object_pk=obj.id)
