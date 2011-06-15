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
import transmeta

from django.core.mail import EmailMultiAlternatives
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import simplejson
from django.template import defaultfilters, RequestContext
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site

from merengue.base.forms import BaseAdminModelForm, BaseForm
from merengue.registry.fields import ConfigFormField
from plugins.contactform.models import SentContactForm


class ContactFormForm(BaseForm):

    def __unicode__(self):
        return self.as_table()

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

        opts_to_save = {}
        opts_to_send = {}
        files = {}
        for opt in contact_form.opts.all():
            val = data.get('option_%s' % opt.id, _('Unset'))
            if val is None:
                val = ''
            label_field = transmeta.get_real_fieldname('label', settings.LANGUAGE_CODE)
            label = defaultfilters.slugify(getattr(opt, label_field))
            if opt.field_type == 'file':
                files[label] = val
            else:
                opts_to_send[opt.label] = val
                opts_to_save[label] = val
        contactuser = {}
        opts_to_save[u'subject'] = subject
        if request.user.is_authenticated():
            opts_to_save[u'user'] = request.user.username
            contactuser[u'name'] = request.user.get_full_name()
            contactuser[u'username'] = request.user.username
        else:
            opts_to_save[u'user'] = 'Anonymous'
            contactuser[u'name'] = _('Anonymous')
            contactuser[u'username'] = 'anonymous'

        opts_to_save[u'mailfrom'] = from_mail
        sent = SentContactForm(contact_form=contact_form,
                                sent_msg=simplejson.dumps(opts_to_save,
                                                            cls=DateTimeAwareJSONEncoder))
        if request.user.is_authenticated():
            sent.sender = request.user
        sent.save()

        html_content = render_to_string('contactform/email.html',
                                        {'opts': opts_to_send,
                                            'site_domain': Site.objects.get_current().domain,
                                            'content': content,
                                            'contact_form': contact_form,
                                            'contactuser': contactuser},
            context_instance=RequestContext(request))

        def mailstr_to_list(mailstr):
            return map(unicode.strip, mailstr.split(','))

        to_mail = mailstr_to_list(contact_form.email)
        bcc_mail = mailstr_to_list(contact_form.bcc)

        attachs = [(f.name, f.read(), f.content_type) for f in files.values() if f]
        plain_content = defaultfilters.striptags(html_content)
        email = EmailMultiAlternatives(subject, plain_content, from_mail,
                                        to_mail, bcc=bcc_mail,
                                        attachments=attachs)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return sent


class SentContactAdminModelForm(BaseAdminModelForm):

    def __init__(self, *args, **kwargs):
        super(SentContactAdminModelForm, self).__init__(*args, **kwargs)
        sent_msg_field = self.fields['sent_msg']
        self.fields['sent_msg'] = ConfigFormField(label=sent_msg_field.label,
                                                  help_text=sent_msg_field.help_text)
        if self.instance:
            sent_msg = self.instance.sent_msg
            from merengue.registry.params import Single, Bool
            config = {}
            for key, val in sent_msg.items():
                if isinstance(val, bool):
                    config[key] = Bool(name=key, label=key, default=val)
                else:
                    config[key] = Single(name=key, label=key, default=val)
                config[key].value = val
            self.fields['sent_msg'].set_config(config)
