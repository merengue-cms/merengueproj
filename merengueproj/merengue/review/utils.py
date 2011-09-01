from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext
from django.utils.importlib import import_module

from transmeta import get_real_fieldname


def get_reviewers(obj):
    path = settings.REVIEWERS_EXTRACTOR
    try:
        mod_name, function_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing email backend module %s: "%s"'
                                    % (mod_name, e)))
    try:
        function = getattr(mod, function_name)
    except AttributeError:
        raise ImproperlyConfigured(('Module "%s" does not define a '
                                    '"%s" function' % (mod_name, function_name)))
    return function(obj)


def send_mail_content_as_pending(obj, review_task, users=None,
                                 template='review/email_as_pending.html'):
    """
    Send a notification mail about that an object has been created as pending
    """
    if not users:
        users = User.objects.all()
    subject = ugettext(u'%s has been set as pending') % getattr(obj, get_real_fieldname('name'),
                                                                obj.name)
    domain = 'http://%s' % Site.objects.get(id=settings.SITE_ID).domain
    body = render_to_string(template, {
        'content': obj,
        'content_url': '%s%s' % (domain, obj.get_absolute_url()),
        'admin_content_url': '%s%s' % (domain, obj.get_admin_absolute_url()),
        'task_admin_url': '%s%s' % (domain, reverse('admin:review_reviewtask_change',
                                                    args=(review_task.pk,)))})
    from_mail = settings.EMAIL_HOST_USER
    recipers = list(set([user.email for user in users if user.email]))

    for reciper in recipers:
        email = EmailMessage(subject, body, from_mail, [reciper])
        email.content_subtype = "html"
        email.send()
