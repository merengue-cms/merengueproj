from django.forms.fields import Field
from django.forms import ValidationError
from django.utils.translation import ugettext as _

from widgets import CaptchaWidget
from util import VALID_VALUE


class CaptchaField(Field):
    widget = CaptchaWidget

    def clean(self, value):
        if value != VALID_VALUE:
            raise ValidationError(_('Typed characters does not match with the ones in the image'))
