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
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import (RelatedModelAdmin, BaseAdmin,
                                 BaseOrderableAdmin,
                                 OrderableRelatedModelAdmin)
from merengue.base.models import BaseContent

from plugins.contactform.models import ContactForm, ContactFormOpt


class ContactFormAdmin(BaseAdmin):

    exclude = ('content', 'opts')

    #fieldsets = (
    #       ('', {
    #           'fields': ('title', 'description', )
    #       }),
    #       (_('Email config'), {
    #           'fields': ('email', 'subject', 'subject_fixed')
    #       }),
    #       (_('Form config'), {
    #           'classes': ('collapse',),
    #           'fields': ('submit_msg', 'reset_msg', 'reset_button')
    #       }),
    #)


class ContactFormRelatedContactFormOptAdmin(ContactFormAdmin, OrderableRelatedModelAdmin):
    tool_name = 'contact_form_opt'
    tool_label = _('contact form option')
    one_to_one = False
    related_field = 'contact_forms'
    html_fields = tuple('description_%s' % lang_code for lang_code, lang_text in settings.LANGUAGES)


class BaseContentRelatedContactFormAdmin(ContactFormAdmin, RelatedModelAdmin):
    tool_name = 'contact_form'
    tool_label = _('contact form')
    one_to_one = False
    related_field = 'content'

    def save_form(self, request, form, change):
        return super(RelatedModelAdmin, self).save_form(request, form, change)

    def save_model(self, request, obj, form, change):
        super(BaseContentRelatedContactFormAdmin, self).save_model(request, obj, form, change)
        getattr(obj, self.related_field).add(self.basecontent)


def register(site):
    """ Merengue ServiceRequest registration callback """
    site.register_related(ContactForm, BaseContentRelatedContactFormAdmin, related_to=BaseContent)
    site.register_related(ContactFormOpt, ContactFormRelatedContactFormOptAdmin, related_to=ContactForm)
