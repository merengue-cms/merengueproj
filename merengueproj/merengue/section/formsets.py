from django.forms.models import BaseInlineFormSet, save_instance


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
