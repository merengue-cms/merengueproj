from django.conf import settings

from captcha import settings as settings_captcha
from models import Captcha
from fields import CaptchaField
from util import get_random_element_from_queryset, captchify_word, get_random_word, VALID_VALUE


def add_captcha(form_class):

    def add_captcha_decorator(view):

        def view_with_captcha(request, *args, **kwargs):
            if request.method == 'POST':
                if isinstance(form_class, type):
                    try:
                        form = form_class(request.user)
                    except:
                        form = form_class
                else:
                    form = form_class
                if hasattr(form, 'fields'):
                    fields = form.fields
                else:
                    fields = form.base_fields

                for field_name, field in fields.iteritems():
                    if isinstance(field, CaptchaField):
                        captcha_post = request.POST[field_name]
                        captcha_session = request.session.get('captcha_text', None)
                        captcha_settings = getattr(settings, 'CAPTCHA_SETTINGS', None)
                        if captcha_settings:
                            case_sensitive = captcha_settings['CASE_SENSITIVE']
                        else:
                            case_sensitive = settings_captcha.CASE_SENSITIVE
                        if not case_sensitive:
                            if captcha_post:
                                captcha_post = captcha_post.lower()
                            if captcha_session:
                                captcha_session = captcha_session.lower()
                        if captcha_post == captcha_session:
                            mutable_post = request.POST.copy()
                            mutable_post[field_name] = VALID_VALUE
                            request.POST = mutable_post
                        break
            all_captchas = Captcha.objects.all()
            if all_captchas:
                random_captcha = get_random_element_from_queryset(all_captchas)
                request.session['captcha_text'] = captchify_word(random_captcha.text)
                request.session['captcha_extra_image'] = random_captcha.image.path
            else:
                random_captcha = get_random_word(length=6)
                request.session['captcha_text'] = captchify_word(random_captcha)
                request.session['captcha_extra_image'] = '%s/img/captcha_default_extra_image.png' % settings.MEDIA_ROOT
            return view(request, *args, **kwargs)
        return view_with_captcha
    return add_captcha_decorator
