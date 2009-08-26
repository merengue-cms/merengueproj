import re

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import logout as auth_logout
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.views.decorators.cache import never_cache
from django.views.i18n import set_language as django_set_language
from django.views.i18n import javascript_catalog

from cmsutils.cache import get_path_cache_key

from merengue.base.models import BaseContent
from merengue.multimedia.models import BaseMultimedia
from tagging.models import Tag

from merengue.section.models import Section, AppSection, BaseSection
from cmsutils.log import send_error, send_info


def index(request):
    if request.user.is_anonymous():
        filters = {'main_document__status': 'published'}
    else:
        filters = {}
    sections = list(
        AppSection.objects.filter().select_related('main_document'),
    ) + list(
        Section.objects.filter(**filters).select_related('main_document'),
    )
    return render_to_response('portal/index.html',
                              {'sections': sections},
                              context_instance=RequestContext(request))


@never_cache
def try_login(request, redirect_field_name='next'):
    new_get_data = request.GET.copy()
    redirect_to = _get_redirect_to(new_get_data, redirect_field_name)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                message = _('Welcome %s') % user
                if user.is_superuser and has_content_pending():
                    url = reverse('merengue.views.portal.list_pending')
                    message += _('. You have a <a href="%s">pending</a> contents') %(url)
                send_info(request, message)
                if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                    redirect_to = settings.LOGIN_REDIRECT_URL
                # login success
                return HttpResponseRedirect(redirect_to)
            else:
                send_error(request, _('User exists, but it have not active account'))
        else:
            send_error(request, _('Credentials are incorrect'))
    if redirect_to and request.method == 'GET':
        if request.user.is_authenticated():
            login_reason = 'access_denied_to_user'
        else:
            login_reason = 'access_denied_to_anonymous'
    else:
        login_reason = 'login_request'
    return render_to_response('portal/login_form.html',
                              {'login_reason': login_reason},
                              context_instance=RequestContext(request))


def has_content_pending():
    return _content_status()


def _get_subclasses(_class, subclass_list=None):
    subclass_list = subclass_list or []
    if not _class.__subclasses__() and not _class in subclass_list:
        subclass_list.append(_class)
    else:
        for subclass in _class.__subclasses__():
            subclass_list = _get_subclasses(subclass, subclass_list)
    return subclass_list


def _content_status(status='pending', bool=True):
    contents = {}
    basecontent_pending = BaseContent.objects.filter(status=status)
    if not bool:
        key = "%s %s" %(BaseContent._meta.app_label, BaseContent._meta.module_name)
        url = "/admin/pending_contents/%s/" % ('/').join(key.split())
        contents[key] = {'content': basecontent_pending, 'url': url, 'verbose_name': BaseContent._meta.verbose_name}
    elif basecontent_pending and bool:
        return True

    basemultimedia_pending = BaseMultimedia.objects.filter(status=status)
    if not bool:
        key = "%s %s" %(BaseMultimedia._meta.app_label, BaseMultimedia._meta.module_name)
        url = "/admin/pending_multimedia/%s/" % ('/').join(key.split())
        contents[key] = {'content': basemultimedia_pending, 'url': url, 'verbose_name': BaseMultimedia._meta.verbose_name}
    elif basemultimedia_pending and bool:
        return True

    if not bool:
        return contents
    return False


@login_required
def list_pending_redirect(request):
    return HttpResponseRedirect(reverse('merengue.views.portal.list_pending'))


@login_required
def list_pending(request):
    contents = _content_status(bool=False)
    return render_to_response('portal/list_pending.html',
                              {'contents': contents,
                               'query': '?status__exact=pending',
                               'root_path': '/admin/',
                               'admin_extra': True,
                              },
                              context_instance=RequestContext(request))


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
        redirect_to = '%s%s%s' %(redirect_to, sep, params)

    return redirect_to


@never_cache
def logout(request, template_name='registration/logged_out.html'):
    new_get_data = request.GET.copy()

    redirect_to = _get_redirect_to(new_get_data)

    if redirect_to:
        for (re_from, target) in settings.LOGOUT_PROTECTED_URL_REDIRECTS:
            if re.match(re_from, redirect_to):
                redirect_to = target
                break


    auth_logout(request)
    send_info(request, _('Thanks for visit'))
    return HttpResponseRedirect(redirect_to)


@never_cache
def ajax_autocomplete_tags(request, app_name, model):
    cls = models.get_model(app_name, model)
    query_string=request.GET.get("q", None)
    limit = request.GET.get("limit", None)
    tags = Tag.objects.usage_for_model(cls)

    for subclass in cls.__subclasses__():
        tags.extend(Tag.objects.usage_for_model(subclass))
    if query_string:
        tags = [t for t in tags if query_string in t.name]
    if limit:
        tags = tags[:int(limit)]
    return HttpResponse("\n".join(["%s|%d" % (t.name, t.id) for t in tags]))


@never_cache
def set_language(request):
    """ Call default django set_language but set language cookie to advise caching middleware """
    lang_code = request.POST.get('language', None)
    response = django_set_language(request)
    if lang_code:
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        # set the plone cookie
        response.set_cookie(settings.PLONE_LANGUAGE_COOKIE_NAME, lang_code)
    return response


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def invalidate_cache(request):
    path = request.REQUEST.get('path', None)
    if path:
        key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        cache_key = get_path_cache_key(path, key_prefix)
        cache.delete(cache_key)
        request.user.message_set.create(message=_("Cache from this page was invalidated"))
        return HttpResponseRedirect(_get_redirect_to(request.GET, redirect_field_name='path'))
    return HttpResponse('path parameter is needed in HTTP request')


def site_map(request):
    related_fields = ('main_document', 'main_menu', 'secondary_menu', 'interest_menu')
    sections = BaseSection.objects.all().order_by('name_%s' % get_language()).select_related(*related_fields)
    return render_to_response('portal/site_map.html',
                              {'sections': sections},
                              context_instance=RequestContext(request))


def searchform_jsi18n(request):
    cache_key = 'searchform_jsi18n_%s' % get_language()
    if cache_key in cache:
        return cache.get(cache_key)
    else:
        response = javascript_catalog(request, packages=['searchform', 'django.conf'])
        cache.set(cache_key, response, settings.CACHE_MIDDLEWARE_SECONDS)
        return response
