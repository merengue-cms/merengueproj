from plugins.feedback.models import Feedback
from django.contrib.comments.forms import CommentForm
#from captcha.fields import CaptchaField
from django import forms


class CaptchaFeedbackForm(CommentForm):
    # XXX: Add captcha system

    parent_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Feedback
        fields = ('comment', 'user_name', 'user_url', 'user_email', )

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return Feedback

    def get_comment_create_data(self):
        # Use the data of the superclass, and add parent field
        data = super(CaptchaFeedbackForm, self).get_comment_create_data()
        parent_id = self.cleaned_data['parent_id']
        if parent_id:
            data['parent'] = Feedback.objects.get(id=parent_id)
        return data
