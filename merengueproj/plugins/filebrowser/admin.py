from merengue.base.admin import PluginAdmin, RelatedModelAdmin

from plugins.filebrowser.models import Repository, Document


class RepositoryModelAdmin(PluginAdmin):
    ordering = ('name', )


class RepositorySectionModelAdmin(RepositoryModelAdmin, RelatedModelAdmin):

    def queryset(self, request, basecontent=None):
        base_qs = super(RelatedModelAdmin, self).queryset(request)
        if basecontent is None:
            # we override our related content
            basecontent = self.basecontent
        return base_qs.filter(**{'section': basecontent})

    def get_form(self, request, obj=None, **kwargs):
        class_form = super(RepositorySectionModelAdmin, self).get_form(request, obj=None, **kwargs)
        del class_form.base_fields['section']
        return class_form

    def save_model(self, request, obj, form, change):
        obj.section = self.basecontent
        super(RelatedModelAdmin, self).save_model(request, obj, form, change)


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
