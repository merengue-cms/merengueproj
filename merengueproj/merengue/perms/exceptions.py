from django.core.exceptions import PermissionDenied as PermissionDeniedDjango


class PermissionDenied(PermissionDeniedDjango):
    "The user did not have permission to do that"

    def __init__(self, content=None, user=None, perm='view', *args, **kwargs):
        super(PermissionDenied, self).__init__(*args, **kwargs)
        self.content = content
        self.user = user
        self.perm = perm
