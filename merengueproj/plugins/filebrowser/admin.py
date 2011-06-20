import os.path
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import PluginAdmin, RelatedModelAdmin
from plugins.filebrowser.models import Repository, Document


class RepositoryModelAdmin(PluginAdmin):
    ordering = ('name', )


class RepositorySectionModelAdmin(RelatedModelAdmin, RepositoryModelAdmin):

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
    list_display = ('__unicode__', 'repository_name', 'location_exists', )

    def repository_name(self, obj=None):
        return obj.repository.name
    repository_name.short_description = _("Repository")

    def location_exists(self, obj=None):
        return os.path.exists(obj.repository.get_absolute_path(obj.location))
    location_exists.short_description = _("The repository folder exists")
    location_exists.boolean = True

    def get_form(self, request, obj=None, **kwargs):
        form = super(DocumentModelAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            obj_location = os.path.join(obj.repository.get_root_path(), obj.location)
            if not os.path.exists(obj_location):
                msg = _("The location folder does not exist in the database. Save the document to create it.")
                form.base_fields['location'].help_text = msg
        return form


def register(site):
    """ Merengue admin registration callback """
    site.register(Repository, RepositoryModelAdmin)
    site.register(Document, DocumentModelAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Repository)
    site.unregister(Document)
