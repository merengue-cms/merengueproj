from copy import copy

from django.db.models import Q
from django.core.exceptions import FieldError
from django.template import TemplateSyntaxError, Library, Node, Context
from django.template.defaulttags import RegroupNode

from cmsutils.adminfilters import QueryStringManager
from merengue.collection.models import Collection, FeedCollection
from merengue.collection.utils import get_render_item_template, get_common_field_translated_name


register = Library()


class CollectionIterator(list):

    def __iter__(self):
        for i in super(CollectionIterator, self).__iter__():
            i.content_type_name = i._meta.verbose_name
            yield i


class CollectionItemNode(Node):

    def __init__(self, collection, item, listing=True):
        self.collection = collection
        self.item = item
        self.listing = listing

    def render(self, context):
        collection = self.collection.resolve(context)
        item = self.item.resolve(context)
        display_fields = collection.display_fields.filter(list_field=self.listing).order_by('field_order')

        fields = []
        for df in display_fields:
            display_data = collection.get_displayfield_data(df, item)
            if display_data is not None:
                fields.append(display_data)
        context_copy = copy(context)
        context_copy.update({
            'item': item,
            'collection': collection,
            'fields': fields,
            'listing': self.listing,
        })
        model_collection = collection.get_first_parents_of_content_types()
        if 'render_item_template' in context:
            template = context['render_item_template']
        else:
            template = get_render_item_template(model_collection)
        return template.render(Context(context_copy))


def collectionitem(parser, token):
    firstbits = token.contents.split(None, 2)
    if len(firstbits) != 3:
        raise TemplateSyntaxError("'collectionitems' tag takes three arguments")
    collection = parser.compile_filter(firstbits[1])
    item = parser.compile_filter(firstbits[2])
    return CollectionItemNode(collection, item)
collectionitem = register.tag(collectionitem)


def fullitem(parser, token):
    firstbits = token.contents.split(None, 2)
    if len(firstbits) != 3:
        raise TemplateSyntaxError("'fullitem' tag takes two arguments")
    collection = parser.compile_filter(firstbits[1])
    item = parser.compile_filter(firstbits[2])
    return CollectionItemNode(collection, item, False)
fullitem = register.tag(fullitem)


class CollectionItemsNode(Node):

    def _get_section(self, request, context):
        return getattr(request, 'section', None) or context.get('section', None)

    def _get_items(self, collection, context):
        request = context.get('request', None)
        section = self._get_section(request, context)
        items = collection.get_items(section)
        ignore_filters = request and request.GET.get('__ignore_filters', None)
        if not ignore_filters:
            if request:
                items = self._filter_by_request(request, items)
            if context:
                items = self._filter_by_context(context, items)
            result = items
        elif isinstance(items, list):
            result = Collection.objects.none()
            for queryset in items:
                result |= queryset
        else:
            result = items
        return items

    def _filter_by_multiple_filters(self, queryset, filters):
        if isinstance(filters, dict):
            for key, value in filters.items():
                try:
                    queryset = queryset.filter(**{key: value})
                except FieldError:
                    continue
        elif isinstance(filters, Q):
            queryset = queryset.filter(filters)
        return queryset

    def _filter_by_filters(self, items, filters):
        if isinstance(items, list):
            result = []
            for queryset in items:
                queryset = self._filter_by_multiple_filters(queryset, filters)
                if hasattr(queryset, '__iter__'):
                    result += list(queryset)
                else:
                    result.append(queryset)
        else:
            result = self._filter_by_multiple_filters(items, filters)
        return result

    def _filter_by_request(self, request, items):
        qsm = QueryStringManager(request, page_var='page', ignore_params=('set_language', ))
        filters = qsm.get_filters()
        return self._filter_by_filters(items, filters)

    def _filter_by_context(self, context, items):
        filters = context.get('_filters_collection', {})
        return self._filter_by_filters(items, filters)

    def __init__(self, collection, var_name):
        self.collection = collection
        self.var_name = var_name

    def render(self, context):
        collection = self.collection.resolve(context)
        if isinstance(collection, FeedCollection):
            context.update({self.var_name: collection.get_items()})
            return ''
        items = self._get_items(collection, context)
        context.update({self.var_name: items})

        group_by_attr = get_common_field_translated_name(collection, collection.group_by)
        order_by_attr = get_common_field_translated_name(collection, collection.order_by)

        if not group_by_attr and not order_by_attr:
            return ''

        if not order_by_attr and group_by_attr:
            items = items.order_by(group_by_attr)
            context.update({self.var_name: list(items)})
            return ''

        if not group_by_attr:
            if collection.reverse_order:
                result = items.order_by('-%s' % order_by_attr)
            else:
                result = items.order_by(order_by_attr)
            context.update({self.var_name: result})
            return ''

        items_grouped = list(items.order_by(group_by_attr))
        items_ordered = list(items.order_by(order_by_attr))

        def sorting(x, y):
            first = cmp(items_grouped.index(x), items_grouped.index(y))
            if first:
                return first
            second = cmp(items_ordered.index(x), items_ordered.index(y))
            if collection.reverse_order:
                return -second
            return second

        result = list(items)
        result.sort(sorting)
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
        if isinstance(collection, FeedCollection):
            self.expression = self.parser.compile_filter('group_field')
        else:
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
