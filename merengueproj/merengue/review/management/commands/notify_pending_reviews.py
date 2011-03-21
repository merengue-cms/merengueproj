from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.translation import ugettext
from django.template.loader import render_to_string

from merengue.base.management.base import MerengueCommand
from merengue.review.models import ReviewTask


class Command(MerengueCommand):
    help = "Send a mail with the not reviewed tasks"

    def handle(self, **options):
        not_reviewed = ReviewTask.objects.filter(is_done=False)

        for user in User.objects.all():
            not_reviewed = ReviewTask.objects.filter(is_done=False, assigned_to=user)
            if not_reviewed:
                subject = ugettext(u'You have pending tasks')
                body = render_to_string('review/email_reminder_list.html',
                                        {'content_list': not_reviewed,
                                         'username': user.username})
                from_mail = settings.EMAIL_HOST_USER
                send_mail(subject, body, from_mail, [user.email], fail_silently=False)
