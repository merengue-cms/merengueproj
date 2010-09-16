from merengue.base.admin import BaseAdmin

from plugins.filebrowser.models import Repository, Document


class RepositoryModelAdmin(BaseAdmin):
    ordering = ('name', )


class DocumentModelAdmin(BaseAdmin):
    ordering = ('id', )


def register(site):
    """ Merengue admin registration callback """
    site.register(Repository, RepositoryModelAdmin)
    site.register(Document, DocumentModelAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Repository)
    site.unregister(Document)
