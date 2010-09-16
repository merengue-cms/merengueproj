import os

from django.db import models
from django.db.models.query import QuerySet


class RepositoryManager(models.Manager):

    def get(self, *args, **kwargs):
        repository = super(RepositoryManager, self).get(*args, **kwargs)
        assert os.path.isdir(repository.get_root_path()), \
            'Root directory for "%s" repository does not exists' % repository
        return repository


class DocumentQuerySet(QuerySet):

    def visible_by_user(self, user):
        """
        Documents visibles by user.
        A superuser will see all contents. Others user will see entries in a community that user is member
        """
        if user.is_superuser:
            return self.all()
        from communities.models import Community
        return self.filter(repository__community__in=Community.objects.with_member(user))


class DocumentManager(models.Manager):

    def get_query_set(self):
        return DocumentQuerySet(self.model)


class FileDocumentQuerySet(QuerySet):

    def visible_by_user(self, user):
        """
        FileDocuments visibles by user.
        A superuser will see all contents. Others user will see entries in a community that user is member
        """
        if user.is_superuser:
            return self.all()
        from communities.models import Community
        return self.filter(document__repository__community__in=Community.objects.with_member(user))


class FileDocumentManager(models.Manager):

    def get_query_set(self):
        return FileDocumentQuerySet(self.model)
