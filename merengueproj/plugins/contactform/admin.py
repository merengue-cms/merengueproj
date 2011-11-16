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

from django.contrib import admin
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import (RelatedModelAdmin, BaseAdmin,
                                 BaseOrderableAdmin, BaseContentAdmin)
from merengue.base.models import BaseContent

from plugins.contactform.forms import SentContactAdminModelForm
from plugins.contactform.models import (ContactForm, ContactFormOpt,
                                        SentContactForm,
                                        ContactFormSelectOpt)


class ContactFormAdmin(BaseAdmin):
    exclude = ('content', )
    html_fields = ('description', )


class SelectInline(admin.TabularInline):
    model = ContactFormSelectOpt
    fk_name = "option"


class ContactFormOptAdmin(BaseOrderableAdmin, BaseAdmin):

    sortablefield = 'order'
    html_fields = ('help_text', )

    inlines = [
        SelectInline,
    ]


class SentContactFormAdmin(BaseAdmin):
    list_display = ('contact_form', 'sender', 'sent_date')
    list_filter = ('contact_form', 'sender', 'sent_date')
    search_fields = ('sent_msg', )


class ContactFormRelatedContactFormOptAdmin(RelatedModelAdmin,
                                            ContactFormOptAdmin):
    tool_name = 'contact_form_opt'
    tool_label = _('contact form option')
    one_to_one = False
    related_field = 'contact_form'


class ContactFormRelatedSentContactFormAdmin(SentContactFormAdmin, RelatedModelAdmin):
    tool_name = 'sent_contact'
    tool_label = _('sent contact form')
    list_display = SentContactFormAdmin.list_display[1:]
    list_filter = SentContactFormAdmin.list_filter[1:]
    one_to_one = False
    related_field = 'contact_form'
    form = SentContactAdminModelForm

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return super(ContactFormRelatedSentContactFormAdmin, self).has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return super(SentContactFormAdmin, self).has_add_permission(request)


class BaseContentRelatedContactFormAdmin(ContactFormAdmin, RelatedModelAdmin):
    tool_name = 'contact_form'
    tool_label = _('contact form')
    one_to_one = False
    related_field = 'content'
    filter_or_exclude = 'filter'

    def save_form(self, request, form, change):
        return super(RelatedModelAdmin, self).save_form(request, form, change)

    def save_model(self, request, obj, form, change):
        super(BaseContentRelatedContactFormAdmin, self).save_model(request, obj, form, change)
        getattr(obj, self.related_field).add(self.basecontent)


class ContactFormRelatedBaseContentAdmin(RelatedModelAdmin):

    def queryset(self, request, basecontent=None):
        base_qs = super(RelatedModelAdmin, self).queryset(request)
        if basecontent is None:
            # we override our related content
            basecontent = self.basecontent
        filter_exclude = {self.related_field: basecontent}
        if self.filter_or_exclude == 'filter':
            return base_qs.filter(**filter_exclude)
        else:
            return base_qs.exclude(**filter_exclude)

    def save_form(self, request, form, change):
        return super(RelatedModelAdmin, self).save_form(request, form, change)

    def save_model(self, request, obj, form, change):
        super(ContactFormRelatedBaseContentAdmin, self).save_model(request, obj, form, change)
        getattr(obj, self.related_field).add(self.basecontent)


class BaseContentRelatedAssociatedContactFormAdmin(ContactFormRelatedBaseContentAdmin):
    tool_name = 'associated_content_related'
    tool_label = _('associated content related')
    related_field = 'contact_form'
    filter_or_exclude = 'exclude'

    actions = BaseContentAdmin.actions + ['associated_content_related']

    def associated_content_related(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            if request.POST.get('post', False):
                for obj in queryset:
                    obj.contact_form.add(self.basecontent)
                msg = ugettext(u"Successfully associated")
                self.message_user(request, msg)
            else:
                extra_context = {'title': ugettext(u'Are you sure you want to associate this items?'),
                                 'action_submit': 'associated_content_related'}
                return self.confirm_action(request, queryset, extra_context)
    associated_content_related.short_description = _("Associated content related")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return super(BaseContentRelatedAssociatedContactFormAdmin, self).has_add_permission(request)


class BaseContentRelatedDisassociatedContactFormAdmin(ContactFormRelatedBaseContentAdmin):
    tool_name = 'disassociated_content_related'
    tool_label = _('disassociated content related')
    related_field = 'contact_form'
    filter_or_exclude = 'filter'

    actions = ContactFormAdmin.actions + ['disassociated_content_related']

    def disassociated_content_related(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            if request.POST.get('post', False):
                for obj in queryset:
                    obj.contact_form.remove(self.basecontent)
                msg = ugettext(u"Successfully disassociated")
                self.message_user(request, msg)
            else:
                extra_context = {'title': ugettext(u'Are you sure you want to disassociate this items?'),
                                 'action_submit': 'disassociated_content_related'}
                return self.confirm_action(request, queryset, extra_context)
    disassociated_content_related.short_description = _("Disassociated content related")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return super(BaseContentRelatedDisassociatedContactFormAdmin, self).has_add_permission(request)


def register(site):
    """ Merengue ServiceRequest registration callback """
    site.register_related(ContactForm, BaseContentRelatedContactFormAdmin, related_to=BaseContent)
    site.register_related(ContactFormOpt, ContactFormRelatedContactFormOptAdmin, related_to=ContactForm)
    site.register_related(SentContactForm, ContactFormRelatedSentContactFormAdmin, related_to=ContactForm)

    site.register_related(BaseContent, BaseContentRelatedAssociatedContactFormAdmin, related_to=ContactForm)
    site.register_related(BaseContent, BaseContentRelatedDisassociatedContactFormAdmin, related_to=ContactForm)


def unregister(site):
    site.unregister_related(ContactForm, BaseContentRelatedContactFormAdmin, related_to=BaseContent)
    site.unregister_related(ContactFormOpt, ContactFormRelatedContactFormOptAdmin, related_to=ContactForm)
    site.unregister_related(SentContactForm, ContactFormRelatedSentContactFormAdmin, related_to=ContactForm)
