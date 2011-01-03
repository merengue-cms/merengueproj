from merengue.base.admin import PluginAdmin

from plugins.filebrowser.models import Repository, Document


class RepositoryModelAdmin(PluginAdmin):
    ordering = ('name', )


class DocumentModelAdmin(PluginAdmin):
    ordering = ('id', )


def register(site):
    """ Merengue admin registration callback """
    site.register(Repository, RepositoryModelAdmin)
    site.register(Document, DocumentModelAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Repository)
    site.unregister(Document)
