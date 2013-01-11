from django.conf import settings

if 'django.contrib.messages' in settings.INSTALLED_APPS:
    from django.contrib import messages

    def send_msg(request, msg, level='error', extra_tags=''):
        messages.add_message(request, level, msg, extra_tags=extra_tags)

    def send_info(request, msg):
        send_msg(request, msg, messages.INFO, 'infomsg')

    def send_error(request, msg):
        send_msg(request, msg, messages.ERROR, 'errormsg')
else:
    from cmsutils.log import send_info, send_msg  # pyflakes:ignore
