from django import template
from django.conf import settings

from merengue.base.models import BaseContent
from merengue.section.models import Section
from merengue.block.blocks import Block, ContentBlock, SectionBlock
from merengue.block.models import RegisteredBlock


register = template.Library()


class RenderBlocksNode(template.Node):

    def __init__(self, place, obj):
        self.place = place
        self.obj = obj

    def render(self, context):
        request = context.get('request', None)
        try:
            obj = None
            if self.obj is not None:
                obj = self.obj.resolve(context)
            rendered_blocks = []
            registered_blocks = RegisteredBlock.objects.actives(ordered=True)
            for registered_block in registered_blocks:
                if registered_block.print_block(self.place):
                    block = registered_block.get_registry_item_class()
                    if issubclass(block, Block) and not obj:
                        rendered_blocks.append(block.render(request,
                                                            self.place,
                                                            context))
                    elif issubclass(block, ContentBlock) and obj is not None and isinstance(obj, BaseContent):
                        rendered_blocks.append(block.render(request,
                                                            self.place,
                                                            obj,
                                                            context))
                    elif issubclass(block, SectionBlock) and obj is not None and isinstance(obj, Section):
                        rendered_blocks.append(block.render(request,
                                                            self.place,
                                                            obj,
                                                            context))
            return "<div class='blockContainer'>%s" \
                   "<input type=\"hidden\" class=\"blockPlace\" value=\"%s\">" \
                   "</div>" \
                   % ('\n'.join(rendered_blocks), self.place)
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='render_blocks')
def do_render_blocks(parser, token):
    """
    Usage::
      render_blocks "leftsidebar"
      render_blocks "rightsidebar" for obj
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) not in [2, 4]:
        raise template.TemplateSyntaxError('"%r" tag requires at two or four '
                                           'arguments' % tag_name)
    if len(bits) == 4 and bits[2] != 'for':
        raise template.TemplateSyntaxError('"%r" statements should use the '
                                           'format %r "leftsidebar" for '
                                           'obj' % (tag_name, tag_name))
    place = bits[1]
    if len(bits) == 2:
        obj = None
    else:
        obj = parser.compile_filter(bits[3])
    if not (place[0] == place[-1] and place[0] in ('"', "'")):
        raise (template.TemplateSyntaxError, "%r tag's argument should be in "
                                             "quotes" % tag_name)
    return RenderBlocksNode(place[1:-1], obj)


@register.inclusion_tag('blocks/header.html', takes_context=True)
def render_blocks_media(context):
    if 'user' in context and context['user'].is_staff:
        return {'is_staff': True,
                'MEDIA_URL': settings.MEDIA_URL}
    else:
        return {'is_staff': False}
