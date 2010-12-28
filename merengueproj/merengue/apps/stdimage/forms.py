from django.forms.fields import ImageField

from stdimage.globals import DELETED


class StdImageFormField(ImageField):

    def clean(self, data, initial=None):
        if data != DELETED:
            return super(StdImageFormField, self).clean(data, initial)
        else:
            return data
