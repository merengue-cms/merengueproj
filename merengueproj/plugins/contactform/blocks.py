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
from django.utils.translation import ugettext as _, ugettext_lazy

from merengue.block.blocks import ContentBlock

from plugins.contactform.models import ContactForm


class ContactFormBlock(ContentBlock):
    name = 'contactform'
    default_place = 'aftercontent'
    help_text = ugettext_lazy('Block with contact form')
    verbose_name = ugettext_lazy('Contact Form Block')

    def render(self, request, place, content, context, *args, **kwargs):

        try:
            contact_form = ContactForm.objects.filter(content=content)[0]
        except IndexError:
            return ''

        form = contact_form.get_form(request)
        errors = request.session.pop('form_errors', {})
        data = request.session.pop('form_data', {})
        if data:
            form._errors = errors
            form.data = data
            form.is_bound = True

        context = dict(content=content,
                       contact_form=contact_form,
                       admin_media=settings.ADMIN_MEDIA_PREFIX,
                       form=form)

        return self.render_block(request, template_name='contactform/block_form.html',
                                 block_title=_('Contact form'),
                                 context=context)
