# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns

urlpatterns = patterns('captcha.views',
    (r'captcha_text_image.png$', 'captcha_text_image'),
    (r'captcha_extra_image.png$', 'captcha_extra_image'),
)
