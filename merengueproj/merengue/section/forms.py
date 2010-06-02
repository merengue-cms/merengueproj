from django import forms
from django.conf import settings
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from merengue.base.forms import BaseAdminModelForm
from merengue.section.models import DocumentSection, Menu
from cmsutils.forms import widgets


class DocumentSectionForm(forms.ModelForm):

    class Meta:
        model = DocumentSection

    def __init__(self, *args, **kwargs):
        super(DocumentSectionForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name.startswith('body'):
                field.widget = widgets.TinyMCE(extra_mce_settings={'inplace_edit': True, 'height': 120, })


class MenuAdminModelForm(BaseAdminModelForm):

    def clean(self):
        cleaned_data = super(MenuAdminModelForm, self).clean()
        if 'slug' in cleaned_data and cleaned_data['slug']:
            if self.section:
                menu_root = self.section.main_menu
            else:
                menu_root = Menu.tree.get(slug=settings.MENU_PORTAL_SLUG)
            same_slug = menu_root.get_descendants().filter(slug=cleaned_data['slug']).exclude(pk=self.instance.pk)
            if same_slug:
                slug_errors = self.errors.get('slug', ErrorList([]))
                slug_errors.extend(ErrorList([_(u'Please set other slug. This slug has been assigned')]))
                self._errors['slug'] = ErrorList(slug_errors)
        return cleaned_data
