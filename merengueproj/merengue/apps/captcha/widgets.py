from django.conf import settings
from captcha import settings as settings_captcha

from django.forms.widgets import Widget
from django.forms.util import flatatt
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class CaptchaWidget(Widget):

    def render(self, name, value, attrs=None):
        attrs = self.build_attrs(attrs,
            type='text',
            name=name,
            id='id_%s' % name,
        )

        captcha_settings = getattr(settings, 'CAPTCHA_SETTINGS', None)
        if captcha_settings:
            use_extra_image = captcha_settings.get('USE_EXTRA_IMAGE', True)
        else:
            use_extra_image = settings_captcha.USE_EXTRA_IMAGE

        if use_extra_image:
            result = ('<img alt="" src="%s" id="captcha-extra-image"/>' % reverse('captcha.views.captcha_extra_image'),)
        else:
            result = tuple()
        result += (
            '<p id="captcha-comment">%s</p>' % _('Type the word that follows the image'),
            '<img alt="%s" src="%s" id="captcha-image"/>' % (
                _('You need to load images in your browser to be able to register, because of the captcha system.'),
                reverse('captcha.views.captcha_text_image')), '<input%s />' % flatatt(attrs),
        )
        return mark_safe('\n'.join(result))
