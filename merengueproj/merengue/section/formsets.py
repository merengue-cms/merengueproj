from django.forms.models import BaseInlineFormSet, save_instance
from django.forms.util import ValidationError
from django.utils.translation import ugettext_lazy as _


class BaseLinkInlineFormSet(BaseInlineFormSet):

    def save_new(self, form, commit=True):
        fk_attname = self.fk.get_attname()
        kwargs = {fk_attname: self.instance.pk}
        new_obj = self.model(**kwargs)
        if fk_attname == self._pk_field.attname:
            exclude = [self._pk_field.name]
        else:
            exclude = []
        if 'baselink_ptr' in form.cleaned_data and not form.cleaned_data['baselink_ptr']:
            del(form.cleaned_data['baselink_ptr'])
        return save_instance(form, new_obj, exclude=exclude, commit=commit)

    def clean(self):
        data = self.data
        if data.get('contentlink-0-content', None) and data.get('absolutelink-0-url', None) or \
            data.get('viewletlink-0-viewlet', None) and data.get('contentlink-0-content', None) or \
            data.get('viewletlink-0-viewlet', None) and data.get('absolutelink-0-content', None):
            raise ValidationError(_('Sorry you can not select two or more options simultaneously for this menu. Fulfill just one.'))
        elif not data.get('contentlink-0-content', None) and not data.get('absolutelink-0-url', None) and \
                not data.get('viewletlink-0-viewlet', None):
            raise ValidationError(_('Sorry you need to select one options for this menu. Fulfill just one.'))
