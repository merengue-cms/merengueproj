from django.conf import settings
from django.contrib.gis.db.models import GeoManager
from django.contrib.gis.db.models.query import GeoQuerySet
from django.db import connection
from django.db.models import Manager
from django.db.models.query import QuerySet


manager_parent_classes = [Manager]
commentsqueryset_parent_classes = [QuerySet]

if settings.USE_GIS:
    from django.contrib.gis.db.models import GeoManager
    from django.contrib.gis.db.models.query import GeoQuerySet
    manager_parent_classes = [GeoManager]
    commentsqueryset_parent_classes = [GeoQuerySet]


class ManagerMeta(type):

    def __new__(meta, name, bases, dct):
        newbases = list(bases) + manager_parent_classes + [object]
        newbases = tuple(newbases)
        return type.__new__(meta, name, newbases, dct)


class CommentsQuerySetMeta(type):

    def __new__(meta, name, bases, dct):
        newbases = list(bases) + commentsqueryset_parent_classes + [object]
        newbases = tuple(newbases)
        return type.__new__(meta, name, newbases, dct)


class BaseManager:
    """ base manager for all content types """
    __metaclass__ = ManagerMeta

    # XXX: for now we have no customization,
    # but I think in future can be useful


class WorkflowManager(BaseManager):
    """ manager for all objects that have a workflow (a status field) """

    def by_status(self, status):
        return self.filter(status=status)

    def published(self):
        """ only published objects """
        return self.by_status('published')

    def pending(self):
        """ only pending objects """
        return self.by_status('pending')

    def draft(self):
        """ only draft objects """
        return self.by_status('draft')


class CommentsQuerySet:
    __metaclass__ = CommentsQuerySetMeta

    def with_comment_number(self, ordered_by_comment_number=False):
        from django.contrib.contenttypes.models import ContentType
        from threadedcomments.models import FreeThreadedComment
        comments_table = connection.ops.quote_name(FreeThreadedComment._meta.db_table)
        model_table = connection.ops.quote_name(self.model._meta.db_table)
        subquery = """
SELECT COUNT(object_id)
FROM %s
WHERE content_type_id = %%s and object_id = %s.basecontent_ptr_id and is_public""" % (comments_table, model_table)

        ctype = ContentType.objects.get_for_model(self.model)
        extra_args = {
            'select': {'comment_number': subquery},
            'select_params': (ctype.id, ),
            }
        if ordered_by_comment_number:
            extra_args['order_by'] = ('-comment_number', )

        return self.extra(**extra_args)


class CommentsManager(WorkflowManager):

    def get_query_set(self):
        return CommentsQuerySet(self.model)


class BaseContentManager(CommentsManager):
    """ manager for all objects that inherits from BaseContent """

    def different_class_names(self):
        """List with the different values for the attribute class_name"""
        different_values = self.values('class_name').distinct('class_name')
        return [v['class_name'] for v in different_values if v['class_name']]
