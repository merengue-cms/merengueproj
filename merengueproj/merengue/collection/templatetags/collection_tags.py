from django.template import TemplateSyntaxError, Variable, Library
from django.template.defaultfilters import dictsort
from django.template.defaulttags import RegroupNode
from django.db import models

from transmeta import get_real_fieldname, fallback_language


register = Library()


@register.inclusion_tag('collection/collection_item.html', takes_context=True)
def collection_item(context, collection, item):
    display_fields = collection.display_fields.all().order_by('field_order')

    fields = []
    for df in display_fields:
        field_name = df.field_name
        try:
            field = item._meta.get_field(field_name)
            verbose_name = field.verbose_name
        except models.FieldDoesNotExist:
            try:
                lang = fallback_language()
                field = item._meta.get_field(get_real_fieldname(field_name, lang))
                verbose_name = field.verbose_name[:-len(lang) - 1]
            except:
                continue
        fields.append({'name': verbose_name,
                       'value': getattr(item, field_name, None),
                       'safe': df.safe})
    return {
        'item': item,
        'collection': collection,
        'fields': fields,
    }


def collectionsort(value, collection):

    if not collection.group_by and not collection.order_by:
        return value

    def sort_func(x, y):
        first = cmp(Variable(collection.group_by).resolve(x),
                    Variable(collection.group_by).resolve(y))
        if first:
            return first
        second = cmp(Variable(collection.order_by).resolve(x),
                     Variable(collection.order_by).resolve(y))
        if collection.reverse_order:
            return -second
        return second

    if not collection.order_by and collection.group_by:
        return dictsort(value, collection.group_by)

    if not collection.group_by:
        return dictsort(value, collection.order_by)

    result = list(value)
    result.sort(sort_func)
    return result
collectionsort.is_safe = False
register.filter(collectionsort)


class CollectionRegroupNode(RegroupNode):

    def __init__(self, target, collection, var_name, parser):
        self.target, self.collection = target, collection
        self.var_name = var_name
        self.parser = parser

    def render(self, context):
        collection = self.collection.resolve(context, True)
        self.expression = self.parser.compile_filter(collection.group_by)
        return super(CollectionRegroupNode, self).render(context)


def collectionregroup(parser, token):
    firstbits = token.contents.split(None, 3)
    if len(firstbits) != 4:
        raise TemplateSyntaxError("'regroup' tag takes five arguments")
    target = parser.compile_filter(firstbits[1])
    if firstbits[2] != 'in':
        raise TemplateSyntaxError("second argument to 'regroup' tag must be 'in'")
    lastbits_reversed = firstbits[3][::-1].split(None, 2)
    if lastbits_reversed[1][::-1] != 'as':
        raise TemplateSyntaxError("next-to-last argument to 'regroup' tag must"
                                  " be 'as'")

    collection = parser.compile_filter(lastbits_reversed[2][::-1])

    var_name = lastbits_reversed[0][::-1]
    return CollectionRegroupNode(target, collection, var_name, parser)
collectionregroup = register.tag(collectionregroup)
