# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.


import datetime

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import simplejson
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext as _

from plugins.contactform.models import SentContactForm


class ContactFormForm(forms.Form):

        def save(self, request, content, contact_form):
            data = self.cleaned_data
            if contact_form.subject_fixed:
                subject = contact_form.subject
            else:
                subject = data['subject']

            opts = {}
            for opt in contact_form.opts.all():
                opts[opt.label] = data.get('option_%s' % opt.id, _('Unset'))

            if request.user.is_authenticated():
                from_mail = request.user.email
            else:
                from_mail = settings.DEFAULT_FROM_EMAIL

            sentopts = opts.copy()
            sentopts[u'subject'] = subject
            sentopts[u'user'] = request.user.username
            for key, value in sentopts.items():
                if isinstance(value, datetime.datetime) or\
                   isinstance(value, datetime.date):
                    sentopts[key] = value.ctime()
            sent = SentContactForm(contact_form=contact_form,
                                   sent_msg=simplejson.dumps(sentopts))
            sent.save()

            context = dict(opts=opts, content=content,
                           contact_form=contact_form)
            msg = render_to_string('contactform/email.html', context,
                                   context_instance=RequestContext(request))

            to_mail = contact_form.email

            send_mail(subject, msg, from_mail,
                      [to_mail], fail_silently=False)
