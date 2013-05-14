from merengue.perms.exceptions import PermissionDenied
from merengue.section.utils import get_section


def is_owner_or_superuser(request):
    if not request.user.is_authenticated():
        return False
    if request.user.is_superuser:
        return True
    section = get_section(request)
    if section and request.user in section.owners.all():
        return True
    return False


def owner_or_superuser_required(view_func):

    def _decorator(request, *args, **kwargs):
        if not is_owner_or_superuser(request):
            raise PermissionDenied(user=request.user)
        return view_func(request, *args, **kwargs)
    return _decorator
