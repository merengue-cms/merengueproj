from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.html import escape
from django.utils.translation import ugettext
from django.template.loader import render_to_string

from transmeta import get_real_fieldname


def send_mail_content_as_pending(obj, users=None, template='review/email_as_pending.html'):
    """
    Send a notification mail about that an object has been created as pending
    """
    if not users:
        users = User.objects.all()
    subject = ugettext(u'%s has been set as pending') % getattr(obj, get_real_fieldname('name'))
    body = render_to_string(template, {'content': obj})
    from_mail = settings.EMAIL_HOST_USER
    recipers = list(set([user.email for user in users if user.email]))

    for reciper in recipers:
        send_mail(subject, escape(body), from_mail, [reciper], fail_silently=False)
