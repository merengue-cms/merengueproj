# -*- coding: utf-8 -*-

from django.template import Library, Variable
from django.conf import settings

from inplaceeditform.commons import get_adaptor_class
from inplaceeditform.tag_utils import RenderWithArgsAndKwargsNode, parse_args_kwargs

register = Library()


def inplace_js(context, activate_inplaceedit=True):
    return context.update({
            'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
            'activate_inplaceedit': activate_inplaceedit,
    })
register.inclusion_tag("inplaceeditform/inplace_js.html", takes_context=True)(inplace_js)


def inplace_css(context):
    return context.update({
            'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
    })
register.inclusion_tag("inplaceeditform/inplace_css.html", takes_context=True)(inplace_css)


def inplace_media(context):
    return context.update({
            'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
    })
register.inclusion_tag("inplaceeditform/inplace_media.html", takes_context=True)(inplace_media)


class InplaceEditNode(RenderWithArgsAndKwargsNode):

    def prepare_context(self, args, kwargs, context):
        expression_to_show = args[0]
        filters_to_edit = kwargs.get('filters_to_edit', [])

        options = kwargs.get('options', None)
        adaptor = kwargs.get('adaptor', None)
        class_inplace = kwargs.get('class_inplace', None)
        tag_name_cover = kwargs.get('tag_name_cover', None)
        loads_tags = kwargs.get('loads', '').split(':')

        tokens_to_show = expression_to_show.split('|')
        obj_field_name, filters_to_show = tokens_to_show[0], tokens_to_show[1:]
        obj_context, field_name = obj_field_name.split(".")
        obj = Variable(obj_context).resolve(context)
        options = options or {}

        filters_to_edit = filters_to_edit and filters_to_edit.split('|') or []

        class_adaptor = get_adaptor_class(adaptor, obj, field_name)
        request = context.get('request')
        adaptor_field = class_adaptor(field_name, obj,
                                      request, filters_to_show,
                                      filters_to_edit,
                                      class_inplace=class_inplace,
                                      tag_name_cover=tag_name_cover,
                                      loads_tags=loads_tags)

        context = {
            'adaptor_field': adaptor_field,
        }
        return context


@register.tag
def inplace_edit(parser, token):
    args, kwargs = parse_args_kwargs(parser, token)
    return InplaceEditNode(args, kwargs, 'inplaceeditform/inplace_edit.html')
