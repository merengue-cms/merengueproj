from django import forms

from tinyimages.models import TinyImage, TinyFile


class TinyBaseForm(forms.ModelForm):
    pass


class TinyImageForm(TinyBaseForm):

    class Meta:
        model = TinyImage
        fields = ('title', 'image', )


class TinyFileForm(TinyBaseForm):

    class Meta:
        model = TinyFile
        fields = ('title', 'file', )
