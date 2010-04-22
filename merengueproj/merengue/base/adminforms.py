from django import forms


class UploadConfigForm(forms.Form):
    file = forms.FileField()
