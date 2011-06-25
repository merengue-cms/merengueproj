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

import hashlib
import re

from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext as _

from plugins.registration.models import Registration
from plugins.registration.forms import (RegistrationForm, PasswordForm,
                                        get_profile_form, RecoverPasswordForm)

from cmsutils.log import send_info


def register_view(request):
    success = False
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
    else:
        form = RegistrationForm()
    return render_to_response('registration/register.html',
                              {'form': form,
                               'success': success},
                              context_instance=RequestContext(request))


def confirm_register_view(request, username, registration_hash):
    registration = Registration.objects.actives().filter(username=username, registration_hash=registration_hash)
    if not registration.count():
        raise Http404
    registration = registration[0]
    profileform_class = get_profile_form()
    if request.method == 'POST':
        password_form = PasswordForm(request.POST)
        profileform = profileform_class(request.POST, registration=registration)
        if password_form.is_valid() and profileform.is_valid():
            password = password_form.get_password()
            user = profileform.save(password)
            auth_user = authenticate(username=user.username, password=password)
            auth_login(request, auth_user)
            registration.delete()
            send_info(request, _('Welcome %s') % user)
            return HttpResponseRedirect('/')
    else:
        password_form = PasswordForm()
    return render_to_response('registration/confirm_register.html',
                              {'password_form': password_form},
                              context_instance=RequestContext(request))


def password_recovery_view(request):
    success = False
    if request.method == 'POST':
        recover_form = RecoverPasswordForm(request.POST)
        if recover_form.is_valid():
            recover_form.save()
            success = True
    else:
        recover_form = RecoverPasswordForm()
    return render_to_response('registration/password_recovery.html',
                              {'recover_form': recover_form,
                               'success': success},
                              context_instance=RequestContext(request))


def confirm_password_recovery(request, username, recovery_hash):
    user = get_object_or_404(User, username=username)
    if recovery_hash != hashlib.md5('%s-%s-%s' % (user.username, user.password, settings.SECRET_KEY)).hexdigest():
        raise Http404
    if request.method == 'POST':
        password_form = PasswordForm(request.POST)
        if password_form.is_valid():
            password = password_form.get_password()
            user.set_password(password)
            user.save()
            auth_user = authenticate(username=user.username, password=password)
            auth_login(request, auth_user)
            send_info(request, _('Your password has been changed. Welcome back %s') % user)
            return HttpResponseRedirect('/')
    else:
        password_form = PasswordForm()
    return render_to_response('registration/change_password.html',
                              {'password_form': password_form,
                               'user': user},
                              context_instance=RequestContext(request))


def ajax_check_username(request):
    username = request.GET.get('username', '')
    error = False
    if not username:
        error = _("This field is required.")
    elif not re.compile(r'^[\w.@+-]+$').search(username):
        error = _("This value may contain only letters, numbers and @/./+/-/_ characters.")
    elif User.objects.filter(username=username).count() or Registration.objects.actives().filter(username=username).count():
        error = _('Username already in use')
    return HttpResponse(simplejson.dumps({'error': error}), mimetype='text/plain')
