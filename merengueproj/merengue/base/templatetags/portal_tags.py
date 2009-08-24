from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe

register = template.Library()


class URLParserLogNode(template.Node):

    def render(self, context):
        request = context.get('request')
        new_get_data = request.GET.copy()
        new_get_data.pop('set_language', '') # remove double language redirect (see ticket #2995)
        url_parser = request.META['PATH_INFO']
        params = new_get_data.urlencode()
        if params:
            url_parser = '%s?%s' % (url_parser, params)
        return mark_safe(url_parser)


@register.tag
def url_parser_log(parser, token):
    return URLParserLogNode()


class IfCachedPageNode(template.Node):

    def __init__(self, nodelist_true, nodelist_false):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def __repr__(self):
        return "<IfCachedPageNode node>"

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        nodes.extend(self.nodelist_true.get_nodes_by_type(nodetype))
        nodes.extend(self.nodelist_false.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        request = context['request']

        use_cache = False
        if hasattr(request, 'path_cache_key'):
            cached_page = cache.get(request.path_cache_key)
            if cached_page:
                have_query_string = bool(request.META['QUERY_STRING']) and not request.cache_query_string
                if not have_query_string:
                    use_cache = True

        if use_cache:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.tag(name="if_cached_page")
def do_if_cached_page(parser, token):
    """
    It needed to have cmsutils.middleware.I18NFetchFromCacheMiddleware
    middleware in MIDDLEWARE_CLASSES settings

    Usage::

        {% if_cached_page %}
            do stuff
        {% else %}
            do stuff
        {% endif %}

    It need to have request in context (i.e. activate request context
    processor django.core.context_processors.request)
    """
    bits = token.contents.split()
    del bits[0]
    if bits:
        raise template.TemplateSyntaxError("'if_cached_page' statement does not expect arguments")
    nodelist_true = parser.parse(('else', 'endif_cached_page'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif_cached_page', ))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return IfCachedPageNode(nodelist_true, nodelist_false)
