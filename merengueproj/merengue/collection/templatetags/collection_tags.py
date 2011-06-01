# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from copy import copy

from django.db.models import Q
from django.db.models.manager import Manager
from django.conf import settings
from django.core.exceptions import FieldError, ObjectDoesNotExist
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
            # This a code to smarsearch plugin
            searcher_id = request.GET.get('__searcher', None)
            searcher = None
            if searcher_id and 'plugins.smartsearch' in settings.INSTALLED_APPS:
                try:
                    from plugins.smartsearch.models import Searcher
                    searcher = Searcher.objects.get(pk=searcher_id)
                except (ImportError, ObjectDoesNotExist):
                    pass
                if searcher:
                    from autoreports.utils import pre_procession_request, filtering_from_request
                    model = collection.get_first_parents_of_content_types()
                    request_processing = pre_procession_request(request, model)
                    filters, items = filtering_from_request(request_processing, items, searcher)
            # Here end the code to smartsearch plugin
            if not searcher and request:
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

        group_by_attr = context.get('_group_by_collection',
                                    get_common_field_translated_name(collection, collection.group_by))
        order_by_attr = context.get('_order_by_collection', None)
        can_reversed = False
        if not order_by_attr:
            order_by_attr = get_common_field_translated_name(collection, collection.order_by)
            can_reversed = True

        if not group_by_attr and not order_by_attr:
            return ''
        if not order_by_attr and group_by_attr:
            items = items.order_by(group_by_attr)
        elif not group_by_attr:
            if collection.reverse_order and can_reversed:
                order_by_attr = '-%s' % order_by_attr
            items = items.order_by(order_by_attr)
        else:
            if collection.reverse_order and can_reversed:
                order_by_attr = '-%s' % order_by_attr
            items = items.order_by(group_by_attr, order_by_attr)
        if collection.limit:
            items = items[:collection.limit]
        context.update({self.var_name: items})
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

    def _num_group_by(self, value):
        cached_group_by_m2m = getattr(self, 'cached_group_by_m2m', {})
        num_group_by = cached_group_by_m2m.get(value, 0)
        if num_group_by == 0:
            paginator = self.context.get('paginator', None)
            current_page = self.context.get('page_obj', None).number
            for p in range(1, current_page):
                num_group_by += paginator.page(p).object_list.count(value)
        cached_group_by_m2m[value] = (num_group_by + 1)
        self.cached_group_by_m2m = cached_group_by_m2m
        return num_group_by

    def _group_by(self, value, ignore_failures):
        group_by = self.expression.resolve_original(value, ignore_failures)
        if isinstance(group_by, Manager):
            objects_related = group_by.all()
            if objects_related:
                if objects_related.count() == 1:
                    num_group_by = 0
                else:
                    num_group_by = self._num_group_by(value)
                return objects_related[num_group_by]
            return ''
        return group_by

    def render(self, context):
        collection = self.collection.resolve(context, True)
        if isinstance(collection, FeedCollection):
            self.expression = self.parser.compile_filter('group_field')
        else:
            self.expression = self.parser.compile_filter(collection.group_by)
            self.expression.resolve_original = self.expression.resolve
            self.context = context
            self.expression.resolve = self._group_by
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
