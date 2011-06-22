from django.http import HttpResponseRedirect
from django.utils.translation import ugettext

from cmsutils.log import send_info
from merengue.base.utils import get_login_url
from merengue.perms.utils import has_permission


def can_create_new_thread(request, content):
    user = request.user
    if not user:
        login_url = '%s?next=%s' % (get_login_url(),
                                    request.get_full_path())
        return HttpResponseRedirect(login_url)
    elif not has_permission(content, user, 'edit'):
        send_info(request, ugettext('You don\'t have permission to create a new thread'))
        return HttpResponseRedirect(content.get_absolute_url())
    return None
