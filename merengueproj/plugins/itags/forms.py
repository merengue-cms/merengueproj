from django import forms
from django.utils.translation import ugettext

from tagging.models import Tag
from transmeta import get_fallback_fieldname


class ITagForm(forms.ModelForm):

    def clean(self):
        # validate uniqueness of tag names (see #1201)
        cleaned_data = super(ITagForm, self).clean()
        tag_name_field = get_fallback_fieldname('tag_name')
        tag_name = cleaned_data.get(tag_name_field)
        qs = Tag.objects.filter(name=tag_name)
        if self.instance.pk is not None:
            # exclude the current object from the query if we are editing
            qs = qs.exclude(pk=self.instance.pk)
        if qs:
            self._errors[tag_name_field] = self.error_class(
                [ugettext('This tag name already exists')],
            )
            del cleaned_data[tag_name_field]
        return cleaned_data
