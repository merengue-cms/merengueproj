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

from django.conf import settings
from django.db import connection
from django.db.models import Manager
from django.db.models.query import QuerySet


manager_parent_classes = [Manager]
basequeryset_parent_classes = [QuerySet]

# hack to change base class depending on if USE_GIS flag is enabled
if settings.USE_GIS:
    from django.contrib.gis.db.models import GeoManager
    from django.contrib.gis.db.models.query import GeoQuerySet
    manager_parent_classes = [GeoManager]
    basequeryset_parent_classes = [GeoQuerySet]


class ManagerMeta(type):
    """ Metaclass which changes the parent classes depending on if USE_GIS flag is enabled """

    def __new__(meta, name, bases, dct):
        newbases = list(bases) + manager_parent_classes + [object]
        newbases = tuple(newbases)
        return type.__new__(meta, name, newbases, dct)


class BaseQuerySetMeta(type):
    """ Metaclass which changes the parent classes depending on if USE_GIS flag is enabled """

    def __new__(meta, name, bases, dct):
        newbases = list(bases) + basequeryset_parent_classes + [object]
        newbases = tuple(newbases)
        return type.__new__(meta, name, newbases, dct)


class BaseManager:
    """ Base manager for all Merengue content types """
    __metaclass__ = ManagerMeta


class WorkflowManager(BaseManager):
    """ Manager for all objects that have a workflow (a status field) """

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


class BaseContentQuerySet:
    """ Base queryset class for all managed contents (which inherits BaseContent) """
    __metaclass__ = BaseQuerySetMeta

    def visible_by_user(self, user):
        from merengue.perms.utils import has_permission
        for content in self:
            if has_permission(content, user, 'view'):
                yield content

    def editable_by_user(self, user):
        from merengue.perms.utils import has_permission
        for content in self:
            if has_permission(content, user, 'edit'):
                yield content


class CommentsQuerySet:
    """ Base queryset class for comments """
    __metaclass__ = BaseQuerySetMeta

    def with_comment_number(self, ordered_by_comment_number=False):
        """ Add a useful extra attribute with the comments number """
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
    """ Manager for all comments """

    def get_query_set(self):
        return CommentsQuerySet(self.model)


class BaseContentManager(WorkflowManager):
    """ Manager for all objects that inherits from BaseContent """

    def get_query_set(self):
        return BaseContentQuerySet(self.model)

    def visible_by_user(self, user):
        return self.get_query_set().visible_by_user(user)

    def different_class_names(self):
        """List with the different values for the attribute class_name"""
        different_values = self.values('class_name').distinct('class_name')
        return [v['class_name'] for v in different_values if v['class_name']]
