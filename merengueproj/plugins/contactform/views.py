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

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.translation import ugettext as _

from merengue.base.models import BaseContent
from plugins.contactform.models import ContactForm


def contact_form_submit(request, content_slug, contact_form_id):
    content = get_object_or_404(BaseContent, slug=content_slug)
    contact_form = get_object_or_404(ContactForm, pk=contact_form_id,
                                     content__slug=content_slug)

    if request.method == 'POST':
        form = contact_form.get_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if contact_form.subject_fixed:
                subject = contact_form.subject
            else:
                subject = data['subject']

            opts = {}
            for opt in contact_form.opts.all():
                opts[opt.label] = data.get('option_%s' % opt.id, _('Unset'))

            context = dict(opts=opts, content=content,
                           contact_form=contact_form)
            msg = render_to_string('contactform/email.html', context,
                                       context_instance=RequestContext(request))

            if request.user.is_authenticated():
                from_mail = request.user.email
            else:
                from_mail = settings.DEFAULT_FROM_EMAIL

            to_mail = contact_form.email

            send_mail(subject, msg, from_mail,
                      [to_mail], fail_silently=False)

            request.session['form_msg'] = _('Form was sended correctly')
        else:
            # Errors in session because we're redirecting
            err = form.errors
            for k, vs in err.items():
                err[k] = [unicode(v) for v in vs]
            request.session['form_errors'] = err
            request.session['form_data'] = form.data

    return HttpResponseRedirect(content.public_link())
