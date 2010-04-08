from django import template


register = template.Library()


class RenderViewletNode(template.Node):

    def __init__(self, registered_viewlet):
        self.registered_viewlet = registered_viewlet

    def render(self, context):
        request = context.get('request', None)
        try:
            if self.registered_viewlet is not None:
                viewlet = self.registered_viewlet.resolve(context).get_registry_item_class()
            else:
                viewlet = None
            return viewlet.render(request)
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_viewlet')
def do_render_viewlet(parser, token):
    """
    Usage::
      render_viewlet registered_viewlet
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) != 2:
        raise template.TemplateSyntaxError('"%r" tag requires at one argument' % tag_name)
    registered_viewlet = parser.compile_filter(bits[1])
    return RenderViewletNode(registered_viewlet)
