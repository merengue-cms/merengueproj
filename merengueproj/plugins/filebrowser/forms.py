from django import forms
from django.utils.translation import ugettext_lazy as _

from cmsutils.forms import GenericAddForm, GenericEditForm
from cmsutils.forms.wtform import WTForm

from plugins.filebrowser.models import Document
from plugins.filebrowser.templatetags.filebrowser_tags import filebrowser_reverse


class DocMixin(WTForm, forms.ModelForm):
    template = 'filebrowser/doc_edit.html'
    button_label = _('Save')

    class Meta:
        model = Document
        fields = ('title', 'content', )

    def __init__(self, request, *args, **kwargs):
        self.path = kwargs.pop('path', None)
        self.repository = kwargs.pop('repository', None)
        self.url_prefix = kwargs.pop('url_prefix', None)
        super(DocMixin, self).__init__(request, *args, **kwargs)

    def next_url(self, instance):
        return filebrowser_reverse(self.request, 'filebrowser_viewdoc',
            kwargs={'repository_name': instance.repository.name,
                    'doc_slug': instance.slug},
            url_prefix=self.url_prefix)


class AddDocForm(DocMixin, GenericAddForm):
    title_label = _('Create Document')

    def save(self):
        document = GenericAddForm.save(self, commit=False)
        document.location = self.path
        document.repository = self.repository
        if not document.location.endswith('/'):
            document.location += '/'
        document.save()
        return document


class EditDocForm(DocMixin, GenericEditForm):
    pass
