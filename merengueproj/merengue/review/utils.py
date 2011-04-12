from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext
from django.template.loader import render_to_string

from transmeta import get_real_fieldname


def send_mail_content_as_pending(obj, review_task, users=None,
                                 template='review/email_as_pending.html'):
    """
    Send a notification mail about that an object has been created as pending
    """
    if not users:
        users = User.objects.all()
    subject = ugettext(u'%s has been set as pending') % getattr(obj, get_real_fieldname('name'),
                                                                obj.name)
    body = render_to_string(template, {
            'content': obj,
            'task_admin_url': 'http://%s%s' % (Site.objects.get(id=settings.SITE_ID).domain,
                                               reverse('admin:review_reviewtask_change',
                                                       args=(review_task.pk,)))})
    from_mail = settings.EMAIL_HOST_USER
    recipers = list(set([user.email for user in users if user.email]))

    for reciper in recipers:
        email = EmailMessage(subject, body, from_mail, [reciper])
        email.content_subtype = "html"
        email.send()
