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


from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from cmsutils.log import send_info
from merengue.base.models import BaseContent
from plugins.contactform.models import ContactForm


def contact_form_submit(request, content_id, contact_form_id):
    content = get_object_or_404(BaseContent, pk=content_id).get_real_instance()
    contact_form = get_object_or_404(ContactForm, pk=contact_form_id,
                                     content__pk=content_id)

    if request.method == 'POST':
        form = contact_form.get_form(request)
        if form.is_valid():
            sentcontactform = form.save(request, content, contact_form)
            if contact_form.redirect_to:
                redirect = contact_form.redirect_to
                if contact_form.redirect_to_with_params:
                    redirect = "%s?content_id=%s&contact_form_id=%s&sentcontactform=%s" % (redirect,
                                                                                           content.pk,
                                                                                           contact_form_id,
                                                                                           sentcontactform.pk)
            else:
                redirect = request.META.get('HTTP_REFERER',
                                            content.public_link())
            if contact_form.sent_msg:
                send_info(request, contact_form.sent_msg)
        else:
            return errors_to_session(request, content, form, contact_form_id)

    return HttpResponseRedirect(redirect)


def errors_to_session(request, content, form, contact_form_id):
    # Errors in session because we're redirecting
    err = form.errors
    for k, vs in err.items():
        err[k] = [unicode(v) for v in vs]
    request.session['form_errors_%s' % contact_form_id] = err
    request.session['form_data_%s' % contact_form_id] = form.data
    redirect = request.META.get('HTTP_REFERER',
                                content.public_link())
    return HttpResponseRedirect(redirect)
