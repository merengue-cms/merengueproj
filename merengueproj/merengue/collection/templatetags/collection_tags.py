from django.template import Variable, Library
from django.template.defaultfilters import dictsort
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

    if not collection.order_by:
        return dictsort(value, collection.group_by)

    result = list(value)
    result.sort(sort_func)
    return result
collectionsort.is_safe = False
register.filter(collectionsort)
