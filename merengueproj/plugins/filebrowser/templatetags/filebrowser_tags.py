from django.core.urlresolvers import reverse
from django.template.defaulttags import URLNode
from django.template import TemplateSyntaxError, Library
from django.utils.encoding import smart_str

register = Library()


def filebrowser_reverse(view_name, args=None, kwargs=None, url_prefix=None):
    #if 'path' in kwargs and not kwargs['path']:
        #del kwargs['path'] # this fixes an strange error with reverse resolving in some boxes
    if url_prefix is None:
        return reverse(view_name, urlconf=None, args=args, kwargs=kwargs)
    repository_name = kwargs.pop('repository_name')
    url_path = reverse(view_name, urlconf='filebrowser.urls', args=args, kwargs=kwargs)
    return u'%s%s' % (url_prefix, url_path)


class FileBrowserURLNode(URLNode):

    def render(self, context):
        from django.core.urlresolvers import NoReverseMatch
        url_prefix = context.get('url_prefix', None)
        if not url_prefix:
            return super(FileBrowserURLNode, self).render(context)
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        url = ''
        try:
            url = filebrowser_reverse(self.view_name, args=args, kwargs=kwargs, url_prefix=url_prefix)
        except NoReverseMatch:
            if self.asvar is None:
                raise
        return url


def filebrowser_url(parser, token):
    """
    Returns an absolute URL matching given view with its parameters,
    like default url tag.

    But if url_prefix was defined in a view, it overrides URL with this prefix.
    """
    bits = token.contents.split(' ')
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return FileBrowserURLNode(viewname, args, kwargs, asvar)
filebrowser_url = register.tag(filebrowser_url)
