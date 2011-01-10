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

try:
    from functools import update_wrapper
except ImportError:
    from django.utils.functional import update_wrapper  # Python 2.3, 2.4 fallback.

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.http import urlquote

try:
    from django.contrib.auth.decorators import _CheckLogin
except ImportError:
    # Django 1.2 has no _CheckLogin decorator. We copied a old version (from Django 1.1 code)

    class _CheckLogin(object):
        """
        Class that checks that the user passes the given test, redirecting to
        the log-in page if necessary. If the test is passed, the view function
        is invoked. The test should be a callable that takes the user object
        and returns True if the user passes.

        We use a class here so that we can define __get__. This way, when a
        _CheckLogin object is used as a method decorator, the view function
        is properly bound to its instance.
        """

        def __init__(self, view_func, test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
            if not login_url:
                from django.conf import settings
                login_url = settings.LOGIN_URL
            self.view_func = view_func
            self.test_func = test_func
            self.login_url = login_url
            self.redirect_field_name = redirect_field_name

            # We can't blindly apply update_wrapper because it udpates __dict__ and
            # if the view function is already a _CheckLogin object then
            # self.test_func and friends will get stomped. However, we also can't
            # *not* update the wrapper's dict because then view function attributes
            # don't get updated into the wrapper. So we need to split the
            # difference: don't let update_wrapper update __dict__, but then update
            # the (parts of) __dict__ that we care about ourselves.
            update_wrapper(self, view_func, updated=())
            for k in view_func.__dict__:
                if k not in self.__dict__:
                    self.__dict__[k] = view_func.__dict__[k]

        def __get__(self, obj, cls=None):
            view_func = self.view_func.__get__(obj, cls)
            return _CheckLogin(view_func, self.test_func, self.login_url, self.redirect_field_name)

        def __call__(self, request, *args, **kwargs):
            if self.test_func(request.user):
                return self.view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            tup = self.login_url, self.redirect_field_name, path
            return HttpResponseRedirect('%s?%s=%s' % tup)

from merengue.base.models import BaseContent


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):

    def decorate(view_func):
        return _ExtraCheckLogin(view_func, test_func, login_url, redirect_field_name)
    return decorate


def _get_content(request, slug_field, model, *args, **kwargs):
    slug = kwargs.get(slug_field, None)
    content = get_object_or_404(model, slug=slug)
    return content


def content_public_required(view_func=None, slug_field='slug', model=BaseContent, login_url=None):

    def _content_public_required(request, *args, **kwargs):
        content = _get_content(request, slug_field, model, *args, **kwargs)
        is_creator = hasattr(content, 'creator') and content.creator and content.creator.id == request.user.id
        # 2 is published status for documents
        return content.status == 'published' or content.status == 2 or request.user.is_staff or is_creator
    decorator = user_passes_test(_content_public_required, login_url)
    if view_func:
        return decorator(view_func)
    return decorator


class _ExtraCheckLogin(_CheckLogin):

    def __init__(self, view_func, test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
        if not login_url:
            from django.conf import settings
            login_url = settings.LOGIN_URL
        self.view_func = view_func
        self.test_func = test_func
        self.login_url = login_url
        self.redirect_field_name = redirect_field_name
        # Next call is with updated=() because an issue with multiples decorators chained. See #899
        update_wrapper(self, view_func, updated=())

    def __call__(self, request, *args, **kwargs):
        if self.test_func(request, *args, **kwargs):
            return self.view_func(request, *args, **kwargs)
        path = urlquote(request.get_full_path())
        tup = self.login_url, self.redirect_field_name, path
        return HttpResponseRedirect('%s?%s=%s' % tup)


def login_required_or_permission_denied(view_func):

    def _decorator(request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _decorator
