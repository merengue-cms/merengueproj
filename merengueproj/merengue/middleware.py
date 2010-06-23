from django.conf import settings
from django.utils import translation


class LocaleMiddleware(object):
    """
    This middleware checks if we want to change language
    """

    def process_request(self, request):
        forced_lang = request.GET.get('set_language', None)
        if forced_lang:
            translation.activate(forced_lang)
            request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        forced_lang = request.GET.get('set_language', None)
        if forced_lang:
            get = request.GET.copy()
            get.pop('set_language')
            request.GET = get

            if translation.check_for_language(forced_lang):
                if hasattr(request, 'session'):
                    request.session['django_language'] = forced_lang
                else:
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, forced_lang)
        return response


class SimplifiedLayoutMiddleware(object):
    """
    This middleware checks if a simplified page layout is
    requested through a get request parameter and removes
    that parameter from the request in order to not break
    searchers
    """

    def process_request(self, request):
        get = request.GET.copy()
        if request.GET.get('external_view', None):
            request.HIDE_DECORATIONS = True
            request.HIDE_MENU = True
            get.pop('external_view')
        if request.GET.get('menu_view', None):
            request.HIDE_DECORATIONS = True
            get.pop('menu_view')
        request.GET = get


class RemoveRandomAjaxParameter(object):
    """
    This middleware checks if a '_' request parameter is
    set. This parameter is used by jquery to perform non
    cacheable ajax requests in IE.
    """

    def process_request(self, request):
        get = request.GET.copy()
        if request.GET.get('_', None):
            get.pop('_')
        request.GET = get
