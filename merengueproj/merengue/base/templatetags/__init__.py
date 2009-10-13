from django import template


class IfNode(template.Node):
    """ An abstract node for checking things """

    def __init__(self, parser, token):
        bits = list(token.split_contents())
        end_tag = 'end' + bits[0]
        self.if_node = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else':
            self.else_node = parser.parse((end_tag, ))
            parser.delete_first_token()
        else:
            self.else_node = template.NodeList()

    def __repr__(self):
        return '<IfNode>'

    def check(self, context):
        raise NotImplementedError

    def render(self, context):
        if self.check(context):
            return self.if_node.render(context)
        else:
            return self.else_node.render(context)
