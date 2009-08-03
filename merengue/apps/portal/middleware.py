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
