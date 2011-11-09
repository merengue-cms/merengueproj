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

import base64
import datetime
import feedparser
try:
    import cPickle as pickle
except:
    import pickle  # pyflakes:ignore

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Q, permalink
from django.template import defaultfilters
from django.utils.importlib import import_module
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from transmeta import get_real_fieldname, fallback_language

from merengue.base.models import BaseContent
from merengue.section.models import BaseSection
from merengue.collection import filter_funcs
from merengue.collection.exceptions import CollectionWithoutContentTypesException


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
    ('date_lt', _('Less than (for dates objects)')),
    ('gt', _('Greater than')),
    ('gte', _('Greater than or equal')),
    ('date_gt', _('Greater than (for dates objects)')),
    ('in', _('In (coma separated list)')),
    ('isnull', _('Is empty')),
)


def _get_value(field, field_name, item):
    value = getattr(item, field_name, None)
    if not value:
        return value
    for vfilter in field.collectiondisplayfieldfilter_set.all().order_by('filter_order'):
        filter_module_name, filter_module_function = vfilter.filter_module.rsplit('.', 1)
        func = getattr(import_module(filter_module_name), filter_module_function, None)
        if vfilter.filter_params:
            value = func(value, *vfilter.filter_params.split(','))
        else:
            value = func(value)
    return value


class Collection(BaseContent):
    content_types = models.ManyToManyField(
        ContentType,
        verbose_name=_(u'Content Types'),
        blank=True,
        null=True,
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
        verbose_name=_(u'Reverse order'),
        )

    limit = models.PositiveIntegerField(
        verbose_name=_(u'Number of elements '),
        blank=True,
        null=True,
        )

    show_main_image = models.BooleanField(
        default=True,
        verbose_name=_(u'Show main_image of collection items'),
        )

    filtering_section = models.BooleanField(
        default=True,
        verbose_name=_(u'Filtering section'),
        help_text=_(u'If the collection is into a section, filter for the contents of this section'),
        )

    class Meta:
        verbose_name = _(u'Collection')
        verbose_name_plural = _(u'Collections')
        content_view_function = 'merengue.collection.views.collection_view'
        content_view_template = 'collection_view.html'

    def get_exclude_filters(self):
        """@FIXME: Legacy code. Should be refactored"""
        return self.exclude_filters.all()

    def get_include_filters(self):
        """@FIXME: Legacy code. Should be refactored"""
        return self.include_filters.all()

    def _get_items_from_one_source(self, ct):
        model = ct.model_class()
        if not model:
            return []
        query = model.objects.all()
        return self._filter_query(query)

    def _reduce_to_section(self, query, section=None):
        try:
            if isinstance(section, BaseSection):
                query = query.filter(sections=section)
            elif isinstance(section, basestring):
                query = query.filter(sections__slug=section)
        except FieldError:
            pass
        return query

    def _filter_query(self, query):
        for f in self.get_include_filters():
            try:
                query = f.filter_query(query)
            except FieldError:
                continue
        for f in self.get_exclude_filters():
            try:
                query = f.filter_query(query)
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

    def get_items(self, section=None, filtering_section=None):
        content_types = list(self.content_types.all())
        if len(content_types) == 1:
            items = self._get_items_from_one_source(content_types[0])
        else:
            for ct in content_types:
                model = ct.model_class()
                if not model:
                    continue
                if not issubclass(model, BaseContent):
                    items = self._get_items_from_multiple_sources(content_types)
                    return items
            items = self._get_items_from_basecontent(content_types)
        if filtering_section is None:
            filtering_section = self.filtering_section
        if filtering_section:
            items = self._reduce_to_section(items, section)
        return items

    def get_first_parents_of_content_types(self):
        content_types = self.content_types.all()
        ct_len = len(content_types)
        if ct_len == 0:
            raise CollectionWithoutContentTypesException('The collection "%s" should have defined the content types to list' % self)
        elif ct_len == 1:
            return content_types[0].model_class()
        parents_first = []
        for i in range(ct_len - 1):
            model = content_types[i].model_class()
            next_model = content_types[i + 1].model_class()
            parents_first = parents_first or (model and model.mro())
            parents_second = (next_model and next_model.mro()) or []
            for i, parent_first in enumerate(parents_first):
                if parent_first in parents_second:
                    parents_first = parents_first[i:]
                    break
        return parents_first and parents_first[0]

    def get_displayfield_data(self, display_field, item):
        """
        returns dictionary with data that will be processed by collection view
        to display an item as defined in display_field option.
        This method may be overriden in Collection subclasses.
        """
        field_name = display_field.field_name
        if field_name == 'content_type_name':
            verbose_name = ugettext('Content type name')
        else:
            try:
                field = item._meta.get_field(field_name)
                verbose_name = field.verbose_name
            except models.FieldDoesNotExist:
                try:
                    lang = fallback_language()
                    field = item._meta.get_field(get_real_fieldname(field_name, lang))
                    verbose_name = unicode(field.verbose_name)[:-len(lang) - 1]
                except:
                    # TODO: make this except not empty and discriminate errors
                    return None
        return {
            'name': verbose_name,
            'field_name': field_name,
            'show_label': display_field.show_label,
            'value': _get_value(display_field, field_name, item),
            'type': field.get_internal_type(),
            'safe': display_field.safe,
        }

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.get_real_instance())
        return ('merengue.base.views.admin_link', [content_type.id, self.id, ''])


class FeedItem(BaseContent):
    feed_collection = models.ForeignKey('FeedCollection')

    item_id = models.CharField(
        verbose_name=_(u'Item id'),
        max_length=200,
        )

    item_cached = models.TextField(
        verbose_name=_(u'Feed summary cached'),
        blank=True,
        null=True)

    item_complete_cached = models.TextField(
        verbose_name=_(u'Feed detail cached'),
        blank=True,
        null=True)

    last_updated = models.DateTimeField(
        verbose_name=_(u'Last updated'),
        auto_now=True,
        editable=False,
        )

    excluded = models.BooleanField(
        verbose_name=_(u'Excluded'),
        default=False,
        editable=False,
        )

    order_field = models.CharField(
        verbose_name=_(u'Order field'),
        max_length=200,
        blank=True,
        null=True,
        )

    group_field = models.CharField(
        verbose_name=_(u'Group field'),
        max_length=200,
        blank=True,
        null=True,
        )

    class Meta:
        content_view_function = 'merengue.collection.views.feeditem_view'
        content_view_template = 'feeditem_view.html'
        verbose_name = _(u'Feed item')
        verbose_name_plural = _(u'Feed items')

    def get_real_item(self):
        if hasattr(self, '_real_item'):
            return self._real_item
        if not self.item_cached:
            real_item = None
        else:
            real_item = pickle.loads(base64.decodestring(self.item_cached))
        self._real_item = real_item
        return real_item

    def get_owners(self):
        """
        Override the default behavior. It does not use owners field because
        the feed items are created automatically (have no owners). The owners
        will be the same owners of the feed collection
        """
        return self.feed_collection.get_owners()

    def get_full_item(self, field_name=None):
        real_item = self.get_real_item()
        if hasattr(self, '_full_item'):
            return self._full_item
        full_item = None
        if not self.item_complete_cached and field_name:
            url = getattr(real_item, field_name, None)
            if not url:
                return None
            feed = feedparser.parse(url)
            if feed.entries:
                full_item = feed.entries[0]
                self.item_complete_cached = base64.encodestring(pickle.dumps(full_item))
                self.save()
        elif self.item_complete_cached:
            full_item = pickle.loads(base64.decodestring(self.item_complete_cached))
        if not full_item:
            full_item = real_item
        self._full_item = full_item
        return full_item

    @permalink
    def get_admin_absolute_url(self):
        parent_content_type = ContentType.objects.get_for_model(self.feed_collection)
        return ('merengue.base.views.admin_link', [parent_content_type.id, self.feed_collection.id, 'items/%s/' % self.id])

    def get_parent_for_permissions(self):
        return self.feed_collection.get_parent_for_permissions()

    def get_main_section(self):
        return self.feed_collection.get_main_section()

    def breadcrumbs_items(self):
        urls = []
        try:
            first_item = self.breadcrumbs_first_item()
            if first_item:
                urls.append(first_item)
        except ImportError:
            urls = []
        urls.append((unicode(self.feed_collection),
                     self.feed_collection.get_absolute_url()))
        last_item = self.breadcrumbs_last_item()
        if last_item:
            urls.append(last_item)
        return urls


def handle_feed_item_pre_save(sender, instance, **kwargs):
    field_name = get_real_fieldname('name', fallback_language())
    name = getattr(instance, field_name, None)
    if not name:
        return
    slug = defaultfilters.slugify(name)
    slug_num = slug
    n = 2
    filter_param = 'slug__exact'
    filters = {filter_param: slug_num}
    exclude = {}
    if instance.basecontent_ptr:
        exclude = {'id': instance.basecontent_ptr.id}
    while BaseContent.objects.filter(**filters).exclude(**exclude).count():
        slug_num = slug + u'-%s' % n
        filters[filter_param] = slug_num
        n += 1
    instance.slug = slug_num
models.signals.pre_save.connect(handle_feed_item_pre_save, sender=FeedItem)


class FeedCollection(Collection):
    feed_url = models.URLField(
        verbose_name=_(u'URL of the feed'),
        verify_exists=False,
        )

    last_updated = models.DateTimeField(
        verbose_name=_(u'Last updated'),
        blank=True,
        null=True,
        editable=False,
        )

    expire_seconds = models.IntegerField(
        verbose_name=_(u'Seconds to expire cache'),
        help_text=_(u'Seconds from last update to do a new query. 0 to never query again.'),
        default=86400,  # 24 hours
        )

    remove_items = models.BooleanField(
        verbose_name=_(u'Remove items'),
        help_text=_(u'Remove old items when overwritting cache'),
        default=False,
        )

    title_field = models.CharField(
        verbose_name=_(u'Title field'),
        max_length=100,
        help_text=_(u'Field used for naming contents'),
        default='title',
        blank=True,
        null=True,
        )

    detailed_link = models.CharField(
        verbose_name=_(u'Detailed link'),
        max_length=200,
        help_text=_(u'Field that provides a link to a feed with the full content'),
        blank=True,
        null=True,
        )

    external_link = models.CharField(
        verbose_name=_(u'External link'),
        max_length=200,
        help_text=_(u'Field that provides an external link to the full content'),
        default='link',
        blank=True,
        null=True,
        )

    class Meta:
        verbose_name = _(u'Feed collection')
        verbose_name_plural = _(u'Feed collections')
        content_view_function = 'merengue.collection.views.collection_view'
        content_view_template = 'collection_view.html'

    def perform_query(self, apply_options=False, force_update=False):
        now = datetime.datetime.now()
        feed = {'entries': []}
        if (force_update or not self.last_updated or
            (self.expire_seconds and self.last_updated + datetime.timedelta(seconds=self.expire_seconds) < now)):
            feed = feedparser.parse(self.feed_url)
            self.last_updated = datetime.datetime.now()
            if self.remove_items:
                self.purge_items()
            apply_options = True
        if apply_options:
            self.create_feed_items(feed)
            self.save()

    def purge_items(self):
        for item in self.feeditem_set.all():
            item.delete()

    def get_first_parents_of_content_types(self):
        return FeedItem

    def make_single_item(self, feed_item, entry):
        feed_item.item_cached = base64.encodestring(pickle.dumps(entry))
        if self.order_by:
            feed_item.order_field = getattr(entry, self.order_by, None)
        else:
            feed_item.order_field = None
        if self.group_by:
            feed_item.group_field = getattr(entry, self.group_by, None)
        else:
            feed_item.group_field = None
        title_field = self.title_field or 'title'
        field_name = get_real_fieldname('name', fallback_language())
        setattr(feed_item, field_name, getattr(entry, title_field, getattr(entry, 'id', None)))
        feed_item.excluded = self.is_excluded(entry)
        feed_item.save()

    def is_excluded(self, entry):
        for f in self.get_include_filters():
            operator_func = getattr(filter_funcs, '%s_func' % f.filter_operator, None)
            if not operator_func:
                continue
            if not operator_func(getattr(entry, f.filter_field, None), f.filter_value):
                return True
        for f in self.get_exclude_filters():
            operator_func = getattr(filter_funcs, '%s_func' % f.filter_operator, None)
            if not operator_func:
                continue
            if operator_func(getattr(entry, f.filter_field, None), f.filter_value):
                return True
        return False

    def create_feed_items(self, feed):
        entries = feed['entries']
        entries_ids = [i.id for i in entries]
        for i in self.feeditem_set.exclude(item_id__in=entries_ids):
            item = i.get_real_item()
            self.make_single_item(i, item)
        state_published = self.workflow_status.workflow.states.filter(slug='published')
        for entry in entries:
            (item, created) = FeedItem.objects.get_or_create(
                item_id=entry.id,
                feed_collection=self)
            if created and state_published:
                item.workflow_status = state_published[0]
            item.item_complete_cached = None  # Expire details of item if any
            self.make_single_item(item, entry)

    def get_items(self, section=None):
        self.perform_query()  # This only will have some effect if the cache has expired
        return self.feeditem_set.filter(excluded=False).order_by('group_field', 'order_field')

    def get_displayfield_data(self, display_field, item):
        """
        returns dictionary with data that will be processed by collection view
        to display an item as defined in display_field option.
        This method may be overriden in Collection subclasses.
        """
        field_name = display_field.field_name
        if field_name == 'content_type_name':
            verbose_name = ugettext('Content type name')
        else:
            verbose_name = ugettext(display_field.field_name)
        if hasattr(item, 'get_real_item'):
            item = item.get_real_item()
        return {
            'name': verbose_name,
            'field_name': field_name,
            'show_label': display_field.show_label,
            'value': _get_value(display_field, field_name, item),
            'safe': display_field.safe,
        }


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
        blank=True,
        )

    class Meta:
        abstract = True

    def _prepare_in_value(self):
        """
        Custom method that overrides the default behavior for the `in`
        operator
        """
        return self.filter_value.split(',')

    def _prepare_isnull_value(self):
        """
        Custom method that overrides the default behavior for the `isnull`
        operator
        """
        return self.filter_value.lower() == 'true'

    def _prepare_date_lt_value(self):
        """
        Custom method that add a new filter 'date_lt'
        """
        return datetime.datetime.now()

    def _prepare_date_gt_value(self):
        """
        Custom method that add a new filter 'date_gt'
        """
        return datetime.datetime.now()

    def _prepare_value(self):
        """
        The property that returns the actually prepared value of the filter.
        """
        custom_value_method_name = '_prepare_%s_value' % (self.filter_operator)
        if hasattr(self, custom_value_method_name):
            return getattr(self, custom_value_method_name)()
        return self.filter_value

    value = property(_prepare_value)

    def _prepare_q_object(self, field=None, operator=None, value=None):
        """
        Create a simple Q object from the model object. Each statement could be
        overrided by keword arguments.
        """
        if value == None:
            value = self.value
        field_lookup = {
            str('%s__%s' % (field or self.filter_field,
                        operator or self.filter_operator)): value,
        }
        return Q(**field_lookup)

    def _get_isnull_q_object(self):
        """
        Custom method for `in` filter operator.
        """
        isnull_q = self._prepare_q_object()
        is_empty_q = self._prepare_q_object(operator='exact', value="")
        if not self.value:
            return isnull_q & ~is_empty_q
        return isnull_q | is_empty_q

    def _get_date_lt_q_object(self):

        field_lookup = Q(
            (str('%s__lt') % self.filter_field, self.value),
            ) | Q(
            (str('%s__isnull') % self.filter_field, True),
            )

        return field_lookup

    def _get_date_gt_q_object(self):

        field_lookup = Q(
            (str('%s__gt') % self.filter_field, self.value),
            ) | Q(
            (str('%s__isnull') % self.filter_field, True),
            )

        return field_lookup

    def get_q_object(self):
        """
        Common method for creating Q object from the model. Call the custom
        method that overrides the general behavior if exist.
        """
        custom_filter_method_name = '_get_%s_q_object' % (self.filter_operator)
        if hasattr(self, custom_filter_method_name):
            return getattr(self, custom_filter_method_name)()
        return self._prepare_q_object()

    def _filter_isnull_query(self, query):
        # Do no try to filter by __exact='' a non CharField
        try:
            field = query.model._meta.get_field_by_name(self.filter_field)
            field = field and field[0]
        except models.FieldDoesNotExist:
            field = None
        if not field:
            return query
        if hasattr(field, 'get_internal_type') and field.get_internal_type() == 'CharField':
            return query.filter(self.get_q_object())
        else:
            return query.filter(self._prepare_q_object())

    def filter_query(self, query):
        custom_filter_method_name = '_filter_%s_query' % (self.filter_operator)
        if hasattr(self, custom_filter_method_name):
            return getattr(self, custom_filter_method_name)(query)
        return query.filter(self.get_q_object())

    def __unicode__(self):
        return u'%s__%s=%s' % (self.filter_field,
                               self.filter_operator,
                               self.filter_value)


class IncludeCollectionFilter(CollectionFilter):
    collection = models.ForeignKey(
        Collection,
        related_name='include_filters',
        verbose_name=_(u'Collection'),
        )

    class Meta:
        verbose_name = _(u'Include collection filter')
        verbose_name_plural = _(u'Include collection filters')


class ExcludeCollectionFilter(CollectionFilter):
    collection = models.ForeignKey(
        Collection,
        related_name='exclude_filters',
        verbose_name=_(u'Collection'),
        )

    class Meta:
        verbose_name = _(u'Exclude collection filter')
        verbose_name_plural = _(u'Exclude collection filters')

    def filter_query(self, query):
        custom_filter_method_name = '_filter_%s_query' % (self.filter_operator)
        if hasattr(self, custom_filter_method_name):
            return getattr(self, custom_filter_method_name)(query)
        return query.exclude(self.get_q_object())

    def _filter_isnull_query(self, query):
        # Do no try to filter by __exact='' a non CharField
        try:
            field = query.model._meta.get_field_by_name(self.filter_field)
            field = field and field[0]
        except models.FieldDoesNotExist:
            field = None
        if not field:
            return query
        if hasattr(field, 'get_internal_type') and field.get_internal_type() == 'CharField':
            return query.exclude(self.get_q_object())
        else:
            # Excluding a Q object whith isnull doesn't work as expected so we have to exclude by kwarg filter
            return query.exclude(**{'%s__%s' % (str(self.filter_field), str(self.filter_operator)): self.value})


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
    show_label = models.BooleanField(
        default=True,
        verbose_name=_(u'Show field label'),
        )
    list_field = models.BooleanField(
        default=True,
        editable=False,
        )

    class Meta:
        verbose_name = _(u'Collection display field')
        verbose_name_plural = _(u'Collection display fields')

    def __unicode__(self):
        return self.field_name


class CollectionDisplayFieldFilter(models.Model):
    display_field = models.ForeignKey(CollectionDisplayField)

    filter_module = models.CharField(
        max_length=250,
        verbose_name=_(u'Filter module'),
        )

    filter_params = models.CharField(
        max_length=250,
        verbose_name=_(u'Filter params'),
        blank=True,
        default='',
        )

    filter_order = models.IntegerField(
        default=0,
        verbose_name=_(u'Filter order'),
        )

    class Meta:
        verbose_name = _(u'Collection display field filter')
        verbose_name_plural = _(u'Collection display field filters')
