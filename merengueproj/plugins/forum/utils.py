from django.http import HttpResponseRedirect

from merengue.base.utils import get_login_url
from merengue.perms.utils import has_permission


def can_create_new_thread(request, content):
    user = request.user
    if not user:
        login_url = '%s?next=%s' % (get_login_url(),
                                    request.get_full_path())
        return HttpResponseRedirect(login_url)
    elif not has_permission(content, user, 'create_new_thread'):
        return HttpResponseRedirect(content.get_absolute_url())
    return None
