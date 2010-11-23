from django.core.exceptions import FieldError
from django.db import models
from django.template import TemplateSyntaxError, Variable, Library, Node
from django.template.defaultfilters import dictsort
from django.template.defaulttags import RegroupNode

from cmsutils.adminfilters import QueryStringManager
from transmeta import get_real_fieldname, fallback_language


register = Library()


class CollectionIterator(list):

    def __iter__(self):
        for i in super(CollectionIterator, self).__iter__():
            i.content_type_name = i._meta.verbose_name
            yield i


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


class CollectionItemsNode(Node):

    def _get_items(self, collection, context):
        items = collection.get_items()
        request = context.get('request', None)
        ignore_filters = request and request.GET.get('__ignore_filters', None)
        if request and not ignore_filters:
            result = self._filter_by_request(request, items)
        elif isinstance(items, list):
            result = []
            for queryset in items:
                result += list(queryset)
        else:
            result = items
        return CollectionIterator(list(result))

    def _filter_by_multiple_filters(self, queryset, filters):
        for key, value in filters.items():
            try:
                queryset = queryset.filter(**{key: value})
            except FieldError:
                continue
        return queryset

    def _filter_by_request(self, request, items):
        qsm = QueryStringManager(request, page_var='page', ignore_params=('set_language', ))
        filters = qsm.get_filters()
        if isinstance(items, list):
            result = []
            for queryset in items:
                queryset = self._filter_by_multiple_filters(queryset, filters)
                result += list(queryset)
        else:
            result = self._filter_by_multiple_filters(items, filters)
        return result

    def __init__(self, collection, var_name):
        self.collection = collection
        self.var_name = var_name

    def render(self, context):
        collection = self.collection.resolve(context)
        items = self._get_items(collection, context)
        context.update({self.var_name: items})

        if not collection.group_by and not collection.order_by:
            return ''

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
            context.update({self.var_name: dictsort(items, collection.group_by)})
            return ''

        if not collection.group_by:
            result = dictsort(items, collection.order_by)
            if collection.reverse_order:
                result.reverse()
            context.update({self.var_name: result})
            return ''

        result = list(items)
        result.sort(sort_func)
        context.update({self.var_name: result})
        return ''


def collectionitems(parser, token):
    firstbits = token.contents.split(None, 2)
    if len(firstbits) != 3:
        raise TemplateSyntaxError("'collectionitems' tag takes three arguments")
    collection = parser.compile_filter(firstbits[1])
    lastbits_reversed = firstbits[2][::-1].split(None, 2)
    if lastbits_reversed[1][::-1] != 'as':
        raise TemplateSyntaxError("next-to-last argument to 'collectionitems' tag must"
                                  " be 'as'")

    var_name = lastbits_reversed[0][::-1]
    return CollectionItemsNode(collection, var_name)
collectionitems = register.tag(collectionitems)


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
        raise TemplateSyntaxError("'collectionregroup' tag takes five arguments")
    target = parser.compile_filter(firstbits[1])
    if firstbits[2] != 'in':
        raise TemplateSyntaxError("second argument to 'collectionregroup' tag must be 'in'")
    lastbits_reversed = firstbits[3][::-1].split(None, 2)
    if lastbits_reversed[1][::-1] != 'as':
        raise TemplateSyntaxError("next-to-last argument to 'collectionregroup' tag must"
                                  " be 'as'")

    collection = parser.compile_filter(lastbits_reversed[2][::-1])

    var_name = lastbits_reversed[0][::-1]
    return CollectionRegroupNode(target, collection, var_name, parser)
collectionregroup = register.tag(collectionregroup)
