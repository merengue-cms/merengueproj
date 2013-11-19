from django.db import models
from django.utils.translation import ugettext_lazy as _


class Captcha(models.Model):
    text = models.CharField(_(u'text'), max_length="30")
    image = models.ImageField(upload_to='captchas',
                              help_text=_(u'The image must upload at the size that is displayed is not automatically resize'))

    def __unicode__(self):
        return self.text
