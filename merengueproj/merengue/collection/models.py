from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent


FILTER_OPERATORS = (
    ('exact', _('Exact (case-sensitive)')),
    ('iexact', _('Exact (case-insensitive)')),
    ('contains', _('Contains (case-sensitive)')),
    ('icontains', _('Contains (case-insensitive)')),
    ('startswith', _('Starts with (case-sensitive)')),
    ('istartswith', _('Starts with (case-insensitive)')),
    ('endswith', _('Ends with (case-sensitive)')),
    ('iendswith', _('Ends with (case-insensitive)')),
    ('lt', _('Less than')),
    ('lte', _('Less than or equal')),
    ('gt', _('Greater than')),
    ('gte', _('Greater than or equal')),
    ('in', _('In (coma separated list)')),
    ('isnull', _('Is null')),
)


class Collection(BaseContent):
    content_types = models.ManyToManyField(
        ContentType,
        verbose_name=_(u'Content Types'),
        )

    group_by = models.CharField(
        max_length=250,
        verbose_name=_(u'Group by field name'),
        blank=True,
        null=True,
        )

    order_by = models.CharField(
        max_length=250,
        verbose_name=_(u'Order by field name'),
        blank=True,
        null=True,
        )

    reverse_order = models.BooleanField(
        default=False,
        verbose_name=_('Reverse order'),
        )

    class Meta:
        verbose_name = _(u'Collection')
        verbose_name_plural = _(u'Collections')
        content_view_template = 'collection/collection_view.html'

    def get_exclude_filters(self):
        result = []
        for f in self.exclude_filters.all():
            result.append(f.as_dict())
        return result

    def get_include_filters(self):
        result = []
        for f in self.include_filters.all():
            result.append(f.as_dict())
        return result

    def _get_items_from_one_source(self, ct):
        model = ct.model_class()
        query = model.objects.all()
        return self._filter_query(query)

    def _filter_query(self, query):
        for f in self.get_include_filters():
            try:
                query = query.filter(**f)
            except FieldError:
                continue
        for f in self.get_exclude_filters():
            try:
                query = query.exclude(**f)
            except FieldError:
                continue
        return query

    def _get_items_from_multiple_sources(self, content_types):
        results = []
        for ct in content_types:
            results.append(self._get_items_from_one_source(ct))
        return results

    def _get_items_from_basecontent(self, content_types):
        classes = [ct.model for ct in content_types]
        query = BaseContent.objects.filter(class_name__in=classes)
        return self._filter_query(query)

    def get_items(self):
        content_types = self.content_types.all()
        if content_types.count() == 1:
            items = self._get_items_from_one_source(content_types[0])
        else:
            for ct in content_types:
                if not issubclass(ct.model_class(), BaseContent):
                    items = self._get_items_from_multiple_sources(content_types)
                    return items
            items = self._get_items_from_basecontent(content_types)
        return items


class CollectionFilter(models.Model):
    filter_field = models.CharField(
        max_length=250,
        verbose_name=_(u'Filter field name'),
        )
    filter_operator = models.CharField(
        max_length=100,
        verbose_name=_(u'Filter operator'),
        choices=FILTER_OPERATORS,
        )
    filter_value = models.CharField(
        max_length=250,
        verbose_name=_(u'Filter value'),
        )

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s__%s=%s' % (self.filter_field,
                               self.filter_operator,
                               self.filter_value)

    def as_dict(self):
        value = self.filter_value
        try:
            if self.filter_operator == 'in':
                value = value.split(',')
            elif self.filter_operator == 'isnull':
                value = (value.lower() == 'true')
        except:
            pass
        return {'%s__%s' % (self.filter_field,
                            self.filter_operator): value}


class IncludeCollectionFilter(CollectionFilter):
    collection = models.ForeignKey(
        Collection,
        related_name='include_filters',
        verbose_name=_(u'Collection'),
        )


class ExcludeCollectionFilter(CollectionFilter):
    collection = models.ForeignKey(
        Collection,
        related_name='exclude_filters',
        verbose_name=_(u'Collection'),
        )


class CollectionDisplayField(models.Model):
    field_name = models.CharField(
        max_length=250,
        verbose_name=_(u'Field name'),
        )
    field_order = models.IntegerField(
        default=0,
        verbose_name=_(u'Display order'),
        )
    collection = models.ForeignKey(
        Collection,
        verbose_name=_(u'Collection'),
        related_name='display_fields',
        )
    safe = models.BooleanField(
        default=False,
        verbose_name=_(u'Safe html content'),
        )

    def __unicode__(self):
        return self.field_name
