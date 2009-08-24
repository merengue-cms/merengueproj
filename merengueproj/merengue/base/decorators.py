try:
    from functools import update_wrapper
except ImportError:
    from django.utils.functional import update_wrapper  # Python 2.3, 2.4 fallback.

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import _CheckLogin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.http import urlquote

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
