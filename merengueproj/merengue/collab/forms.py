# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.utils.translation import ugettext_lazy as _

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


class CollabTranslationForm(forms.Form):

    languages = forms.ChoiceField(label=_('translation language'))
    translation = forms.CharField(label=_('translation'), widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.content = kwargs.pop('content', None)
        self.is_html = kwargs.pop('is_html', None)
        self.language_code = kwargs.pop('language_code', None)
        self.languages = kwargs.pop('languages', None)
        field = kwargs.pop('field', None)
        self.field = '%s_%s' % (field, self.language_code)
        super(CollabTranslationForm, self).__init__(*args, **kwargs)
        self.fields['languages'].choices=self.languages
        self.fields['languages'].initial=self.language_code
        self.fields['translation'].initial = getattr(self.content, self.field, '')

    def save(self, commit=True):
        setattr(self.content, self.field, self.cleaned_data.get('translation'))
        self.content.save()
