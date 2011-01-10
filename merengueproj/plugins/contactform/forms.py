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

from django.core.mail import EmailMultiAlternatives
from django.core.serializers.json import DateTimeAwareJSONEncoder
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

            if contact_form.sender_email:
                from_mail = data['sender_email']
            else:
                if request.user.is_authenticated():
                    from_mail = request.user.email
                else:
                    from_mail = settings.DEFAULT_FROM_EMAIL

            opts = {}
            files = {}
            for opt in contact_form.opts.all():
                d = data.get('option_%s' % opt.id, _('Unset'))
                if opt.field_type == 'file':
                    files[opt.label] = d
                else:
                    opts[opt.label] = d

            sentopts = opts.copy()
            sentopts[u'subject'] = subject
            if request.user.is_authenticated():
                sentopts[u'user'] = request.user.username
            else:
                sentopts[u'user'] = 'Anonymous'

            sentopts[u'mailfrom'] = from_mail
            sent = SentContactForm(contact_form=contact_form,
                                   sent_msg=simplejson.dumps(sentopts,
                                   cls=DateTimeAwareJSONEncoder))
            if request.user.is_authenticated():
                sent.sender = request.user
            sent.save()

            context = dict(opts=opts, content=content,
                           contact_form=contact_form)
            html_content = render_to_string('contactform/email.html', context,
                context_instance=RequestContext(request))

            def mailstr_to_list(mailstr):
                return map(unicode.strip, mailstr.split(','))

            to_mail = mailstr_to_list(contact_form.email)
            bcc_mail = mailstr_to_list(contact_form.bcc)

            attachs = [(f.name, f.read(), f.content_type) for f in files.values()]
            email = EmailMultiAlternatives(subject, '', from_mail,
                                 to_mail, bcc=bcc_mail,
                                 attachments=attachs)
            email.attach_alternative(html_content, "text/html")

            email.send()
