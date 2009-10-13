from django import template


class IfNode(template.Node):
    """ An abstract node for checking things """

    def __init__(self, if_node, else_node):
        self.if_node = if_node
        self.else_node = else_node

    def __repr__(self):
        return '<IfNode>'

    def check(self, context):
        raise NotImplementedError

    def render(self, context):
        if self.check(context):
            return self.if_node.render(context)
        else:
            return self.else_node.render(context)
