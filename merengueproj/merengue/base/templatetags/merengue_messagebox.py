from django.conf import settings
from django.template import Library
from django.utils.translation import ugettext as _

from merengue.base.log import send_error

register = Library()

if 'django.contrib.messages' in settings.INSTALLED_APPS:
    from django.contrib import messages

    def merengue_messagebox(context):
        request = context['request']
        portal_messages = messages.get_messages(request)
        if not portal_messages:
            if 'form' in context:
                form = context['form']
                if getattr(form, 'errors', []):
                    if form.non_field_errors():
                        send_error(request, form.non_field_errors())
                    send_error(request, _('Form filled has errors. Please correct'))
                    portal_messages = messages.get_messages(request)
        return {'portal_messages': portal_messages}
    messagebox = register.inclusion_tag('base/messagebox.html',
                                       takes_context=True)(merengue_messagebox)
else:
    from cmsutils.templatetags import messagebox as merengue_messagebox
    merengue_messagebox = register.inclusion_tag('cmsutils/messagebox.html',
                                                 takes_context=True)(merengue_messagebox)
