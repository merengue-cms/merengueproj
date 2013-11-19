from django.http import HttpResponse
from util import text_to_captcha_image_data
from django.views.decorators.cache import never_cache


@never_cache
def captcha_text_image(request):
    captcha_text = request.session.get('captcha_text', None)
    image_data, mime_type = text_to_captcha_image_data(captcha_text)
    response = HttpResponse(image_data, mimetype=mime_type)
    response['Cache-Control'] = 'no-cache'
    return response


def captcha_extra_image(request):
    response = HttpResponse(mimetype='image/jpeg')
    response['Cache-Control'] = 'no-cache'
    captcha_extra_image = request.session.get('captcha_extra_image', None)
    if captcha_extra_image:
        image_file = open(captcha_extra_image)
        response.write(image_file.read())
        image_file.close()
    return response
