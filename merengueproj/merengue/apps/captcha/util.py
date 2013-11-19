import os
import random
from django.conf import settings

from captcha import settings as settings_captcha


VALID_VALUE = '__valid__'


def captchify_word(word):
    captcha_settings = getattr(settings, 'CAPTCHA_SETTINGS', None)
    if captcha_settings:
        number_swap = captcha_settings['NUMBER_SWAP']
    else:
        number_swap = settings_captcha.NUMBER_SWAP
    result = ''
    for char in word:
        transformations = [unicode.upper, unicode.lower]
        if char.upper() in number_swap.keys():
            transformations.append(lambda c: number_swap[c.upper()])
        result += random.choice(transformations)(unicode(char))
    return result


def get_random_element_from_queryset(queryset):
    return queryset[random.randint(0, len(queryset) - 1)]


def get_random_word(length=10):
    import string
    result = [random.choice(string.lowercase) for char in xrange(length)]
    return ''.join(result)


def text_to_captcha_image_data(text):
    from captcha.image import CaptchaImage
    try:
        from PIL import ImageFont
    except ImportError:
        import ImageFont  # pyflakes:ignore
    font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), './captcha_font.ttf'), 42)
    captcha = CaptchaImage(text, font)
    captcha.colorize_text(os.path.join(os.path.dirname(__file__), 'bg.png'))
    captcha.make_transparent_bg()
    captcha.deform_text()
    return (captcha.get_image('PNG'), 'image/png')
