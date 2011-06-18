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
    default_caching_params = {
        'enabled': False,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def render(self, request, place, content, context, *args, **kwargs):
        contact_forms = ContactForm.objects.filter(content=content)
        if not contact_forms:
            return ''
        forms = []
        for contact_form in contact_forms:
            form = contact_form.get_form(request)
            errors = request.session.pop('form_errors_%s' % contact_form.pk, {})
            data = request.session.pop('form_data_%s' % contact_form.pk, {})
            if data:
                form._errors = errors
                form.data = data
                form.is_bound = True
            forms.append({'contact_form': contact_form, 'form': form})
        return self.render_block(request, template_name='contactform/block_form.html',
                                 block_title=_('Contact form'),
                                 context={'content': content,
                                          'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
                                          'forms': forms})
