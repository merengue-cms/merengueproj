import copy

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.template import TemplateSyntaxError, TokenParser
from django.templatetags.i18n import TranslateNode
from django.utils.translation import get_language
from django.utils.translation.trans_real import catalog

from rosetta.views import can_translate

register = template.Library()


def get_language_name(lang):
    for lang_code, lang_name in settings.LANGUAGES:
        if lang == lang_code:
            return lang_name


class NotTranslated(object):

    @staticmethod
    def ugettext(cadena):
        raise ValueError("not translated")

    @staticmethod
    def add_fallback(func):
        return


class RosettaTranslateNode(TranslateNode):

    def render(self, context):
        if not ('user' in context and context['user'].is_staff):
            return super(RosettaTranslateNode, self).render(context)

        msgid = self.value.resolve(context)
        cat = copy.copy(catalog())
        cat.add_fallback(NotTranslated)
        styles = ['translatable']
        try:
            msgstr = cat.ugettext(msgid)
        except ValueError:
            styles.append("untranslated")
            msgstr = msgid
        return render_to_string('rosetta/rosetta_trans.html',
                                {'msgid': msgid,
                                 'styles': ' '.join(styles),
                                 'value': msgstr})


def rosetta_trans(parser, token):

    class TranslateParser(TokenParser):

        def top(self):
            value = self.value()
            if self.more():
                if self.tag() == 'noop':
                    noop = True
                else:
                    raise TemplateSyntaxError("only option for 'trans' is 'noop'")
            else:
                noop = False
            return (value, noop)
    value, noop = TranslateParser(token.contents).top()

    return RosettaTranslateNode(value, noop)

register.tag('rosetta_trans', rosetta_trans)


@register.inclusion_tag('rosetta/rosetta_header.html', takes_context=True)
def rosetta_media_inline(context):
    if 'user' in context and context['user'].is_staff:
        return {'is_staff': True,
                'language': get_language_name(get_language())}
    else:
        return {'is_staff': False}


class IfNode(template.Node):

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


class IfCanAccessRosetta(IfNode):

    def check(self, context):
        user = template.Variable('user').resolve(context)
        return can_translate(user)


def if_can_access_rosetta(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 1:
        raise TemplateSyntaxError('%r takes no arguments' % bits[0])
    end_tag = 'end' + bits[0]
    node_if = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        node_else = parser.parse((end_tag, ))
        parser.delete_first_token()
    else:
        node_else = template.NodeList()
    return IfCanAccessRosetta(node_if, node_else)
if_can_access_rosetta = register.tag(if_can_access_rosetta)
