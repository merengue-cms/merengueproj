from django.forms import ValidationError
from django.forms.fields import ImageField

from stdimage.globals import DELETED


class StdImageFormField(ImageField):

    def clean(self, data, initial=None):
        if data != DELETED:
            return super(StdImageFormField, self).clean(data, initial)
        elif self.required and data == DELETED:
            raise ValidationError(self.error_messages['required'])
        else:
            return data
