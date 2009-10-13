from django import template

from merengue.base.templatetags import IfNode

register = template.Library()


@register.inclusion_tag('base/content_title.html', takes_context=True)
def can_edit(context, content):
    return {'content': content, 'request': context.get('request')}


class IfCanEditNode(IfNode):

    def __init__(self, user, content, *args):
        self.content = content
        self.user = user
        super(IfCanEditNode, self).__init__(*args)

    def check(self, context):
        content = template.Variable(self.content).resolve(context)
        user = template.Variable(self.user).resolve(context)
        return bool(content.can_edit(user))


def ifcanedit(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise template.TemplateSyntaxError, '%r takes two arguments' % bits[0]
    user = bits[1]
    content = bits[2]
    end_tag = 'end' + bits[0]
    node_can_edit = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        node_not_can_edit = parser.parse((end_tag, ))
        parser.delete_first_token()
    else:
        node_not_can_edit = template.NodeList()
    return IfCanEditNode(user, content, node_can_edit, node_not_can_edit)
ifcanedit = register.tag(ifcanedit)
