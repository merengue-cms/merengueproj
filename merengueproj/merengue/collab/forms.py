from django import forms

from merengue.collab.models import CollabComment, CollabCommentRevisorStatus


class CollabCommentForm(forms.ModelForm):

    class Meta:
        model = CollabComment
        fields = ('user_name', 'user_email', 'user_url', 'comment_user_type', 'comment', )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.content = kwargs.pop('content', None)
        super(CollabCommentForm, self).__init__(*args, **kwargs)
        if self.request:
            self.user = self.request.user
        else:
            self.user = None

        if self.user and self.user.is_authenticated():
            del(self.fields['user_name'])
            del(self.fields['user_email'])
            del(self.fields['user_url'])
        else:
            self.fields['user_name'].required=True
            self.fields['user_email'].required=True
            self.user = None

    def save(self, commit=True):
        self.instance.user = self.user
        self.instance.content_object = self.content
        self.instance.ip_address = self.request.POST.get('REMOTE_ADDR', '0.0.0.0')
        return super(CollabCommentForm, self).save(commit)


class CollabCommentRevisorStatusForm(forms.ModelForm):

    class Meta:
        model = CollabCommentRevisorStatus
        fields = ('type', 'short_comment', )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.content = kwargs.pop('content', None)
        super(CollabCommentRevisorStatusForm, self).__init__(*args, **kwargs)
        if self.request:
            self.user = self.request.user.is_authenticated() and self.request.user or None
        else:
            self.user = None

    def save(self, commit=True):
        self.instance.revisor = self.user
        self.instance.comment = self.content
        super(CollabCommentRevisorStatusForm, self).save(commit)
