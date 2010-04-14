from django import template
from django.conf import settings

from merengue.block.blocks import Block, ContentBlock
from merengue.block.models import RegisteredBlock


register = template.Library()


class RenderBlocksNode(template.Node):

    def __init__(self, place, content):
        self.place = place
        self.content = content

    def render(self, context):
        request = context.get('request', None)
        try:
            if self.content is not None:
                content = self.content.resolve(context)
            else:
                content = None
            rendered_blocks = []
            registered_blocks = RegisteredBlock.objects.actives(ordered=True)
            for registered_block in registered_blocks:
                if registered_block.print_block(self.place):
                    block = registered_block.get_registry_item_class()
                    if content is None and issubclass(block, Block):
                        rendered_blocks.append(block.render(request,
                                                            self.place))
                    elif content is not None and issubclass(block,
                                                            ContentBlock):
                        rendered_blocks.append(block.render(request,
                                                            self.place,
                                                            content))
            return "<div class='blockContainer'>%s</div>" \
                   % '\n'.join(rendered_blocks)
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_blocks')
def do_render_blocks(parser, token):
    """
    Usage::
      render_blocks "leftsidebar"
      render_blocks "rightsidebar" for content
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) not in [2, 4]:
        raise template.TemplateSyntaxError('"%r" tag requires at two or four '
                                           'arguments' % tag_name)
    if len(bits) == 4 and bits[2] != 'for':
        raise template.TemplateSyntaxError('"%r" statements should use the '
                                           'format %r "leftsidebar" for '
                                           'content' % (tag_name, tag_name))
    place = bits[1]
    if len(bits) == 2:
        content = None
    else:
        content = parser.compile_filter(bits[3])
    if not (place[0] == place[-1] and place[0] in ('"', "'")):
        raise (template.TemplateSyntaxError, "%r tag's argument should be in "
                                             "quotes" % tag_name)
    return RenderBlocksNode(place[1:-1], content)


@register.inclusion_tag('blocks/header.html', takes_context=True)
def render_blocks_media(context):
    if 'user' in context and context['user'].is_staff:
        return {'is_staff': True,
                'MEDIA_URL': settings.MEDIA_URL}
    else:
        return {'is_staff': False}
