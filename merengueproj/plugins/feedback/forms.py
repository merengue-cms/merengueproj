from merengue.base.forms import BaseModelForm

from threadedcomments.models import FreeThreadedComment
from threadedcomments.forms import FreeThreadedCommentForm
#from captcha.fields import CaptchaField


class CaptchaFreeThreadedCommentForm(BaseModelForm, FreeThreadedCommentForm):

    class Meta:
        model = FreeThreadedComment
        fields = ('comment', 'name', 'website', 'email', )

    def __init__(self, user, *args, **kwargs):
        super(CaptchaFreeThreadedCommentForm, self).__init__(*args, **kwargs)
#        if user.is_anonymous():
#            captcha_field = CaptchaField()
#            self.fields['captcha'] = captcha_field
#            self.declared_fields['captcha'] = captcha_field
