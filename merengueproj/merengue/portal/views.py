# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.views import logout as auth_logout
from django.contrib.auth.views import login as auth_login
from django.contrib.auth.views import password_reset as auth_password_reset
from django.contrib.auth.views import password_reset_confirm as auth_password_reset_confirm
from django.contrib.auth.views import password_reset_complete as auth_password_reset_complete
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.i18n import set_language as django_set_language

from merengue.cache import invalidate_cache_for_path
from merengue.perms.decorators import permission_required
from merengue.perms.utils import MANAGE_CACHE_INVALIDATION_PERMISSION

from cmsutils.log import send_info


@never_cache
def login(request, redirect_field_name='next'):
    response = auth_login(request, redirect_field_name=redirect_field_name)
    if request.user.is_authenticated():
        send_info(request, _('Welcome %s') % request.user)
    return response


@never_cache
def logout(request, template_name='registration/logged_out.html'):
    response = auth_logout(request, next_page='/')
    send_info(request, _("Thanks for your visit"))
    return response


def password_reset(request, template_name='registration/password_reset.html',
                            email_template_name='registration/password_reset_email.html'):
    return auth_password_reset(request, template_name=template_name,
                               email_template_name=email_template_name,
                               post_reset_redirect=reverse('website.views.index'))


def password_reset_confirm(request, uidb36=None, token=None, template_name='registration/password_reset_confirm.html'):
    return auth_password_reset_confirm(request, uidb36, token, template_name=template_name,
                                       post_reset_redirect=reverse('website.views.index'))


def password_reset_complete(request, template_name='registration/password_reset.html'):
    return auth_password_reset_complete(request, template_name=template_name,
                                    post_reset_redirect=reverse('website.views.index'))


@never_cache
def set_language(request):
    """ Call default django set_language but set language cookie to advise caching middleware """
    lang_code = request.POST.get('language', None)
    response = django_set_language(request)
    if lang_code:
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


@permission_required(codename=MANAGE_CACHE_INVALIDATION_PERMISSION)
@never_cache
def invalidate_cache(request):
    path = request.REQUEST.get('path', None)
    if path:
        invalidate_cache_for_path(path)
        request.user.message_set.create(message=_("Cache from this page was invalidated"))
        return HttpResponseRedirect(_get_redirect_to(request.GET, redirect_field_name='path'))
    return HttpResponse('path parameter is needed in HTTP request')


# ----- auxiliar functions -----


def _get_redirect_to(new_get_data, redirect_field_name='next'):
    redirect_to = new_get_data.pop(redirect_field_name, '')
    if redirect_to:
        redirect_to = redirect_to.pop()
    params = new_get_data.urlencode()
    if redirect_to.find('?') < 0:
        sep = '?'
    else:
        sep = '&'
    if params:
        redirect_to = '%s%s%s' % (redirect_to, sep, params)

    return redirect_to
