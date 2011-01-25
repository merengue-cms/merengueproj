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

from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from transmeta import TransMeta

from cmsutils.db.fields import JSONField
from merengue.base.models import BaseContent

from plugins.contactform import fields as custom_fields


FIELD_TYPE_CHOICES = (
    ('text', _('Text')),
    ('textarea', _('Text area')),
    ('date', _('Date')),
    ('datetime', _('Datetime')),
    ('checkbox', _('Checkbox')),
    ('radio', _('Radio')),
    ('select', _('Select')),
    ('file', _('File')),
)


class ContactForm(models.Model):

    __metaclass__ = TransMeta

    title = models.CharField(verbose_name=_('name'), max_length=200)
    description = models.TextField(verbose_name=_('description'),
                                   blank=True)
    sent_msg = models.TextField(verbose_name=_('Sent message'),
                                help_text=_('Message to show when the form is sent'),
                                blank=True,
                                default=_('The form was sent correctly'))
    email = custom_fields.ModelMultiEmailField(verbose_name=_('emails'),
                                               default=settings.DEFAULT_FROM_EMAIL,
                                               help_text=_('comma separated email list'))
    bcc = custom_fields.ModelMultiEmailField(verbose_name=_('bcc emails'), blank=True,
                                               help_text=_('comma separated email list'))
    redirect_to = models.CharField(verbose_name=_('redirect to'),
                                   max_length=200,
                                   blank=True)
    subject = models.CharField(verbose_name=_('subject'), max_length=200,
                               default=_('Subject'))
    subject_fixed = models.BooleanField(verbose_name=_('fixed subject'))
    submit_msg = models.CharField(verbose_name=_('submit'), max_length=200,
                                default=_('Send'))
    reset_msg = models.CharField(verbose_name=_('reset'), max_length=200,
                                 default=_('Reset'),
                                 blank=True)
    reset_button = models.BooleanField(verbose_name=_('reset button'),
                                        default=False)

    content = models.ManyToManyField(BaseContent,
                                     verbose_name=_('content'),
                                     related_name='contact_form',
                                     blank=True, null=True)
    captcha = models.BooleanField(verbose_name=_('captcha'), default=True)
    sender_email = models.BooleanField(verbose_name=_('sender email'), default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        translate = ('title', 'description', 'subject', 'submit_msg',
                     'reset_msg', 'sent_msg')
        verbose_name = _('Contact Form')
        verbose_name_plural = _('Contact Forms')

    def get_form(self, request):
        from plugins.contactform.forms import ContactFormForm
        from django import forms
        from django.utils.translation import ugettext as _
        fields = {
            'text': forms.CharField,
            'textarea': custom_fields.TextAreaField,
            'date': custom_fields.DateField,
            'datetime': custom_fields.DateTimeField,
            'checkbox': forms.BooleanField,
            'select': forms.ChoiceField,
            'radio': custom_fields.RadioField,
            'file': forms.FileField,
        }

        if request.method == 'POST':
            f = ContactFormForm(request.POST, request.FILES)
        else:
            f = ContactFormForm()
        index = 0

        if self.sender_email:
            initial = ''
            if request.user.is_authenticated():
                initial = request.user.email
            sender_email = forms.EmailField(_('sender email'),
                                    initial=initial)
            f.fields.insert(index, 'sender_email', sender_email)
            index += 1

        if not self.subject_fixed:
            f.fields.insert(index, 'subject',
                            forms.CharField(label=_('Subject'),
                                            initial=self.subject))
            index += 1

        for opt in self.opts.all():
            Field = fields[opt.field_type]
            help_text = opt.help_text

            if opt.field_type == 'select':
                choices = []
                for choice in opt.choices.all():
                    choices.append((choice.value, choice.label))

                field = Field(label=opt.label, help_text=help_text,
                              required=opt.required, choices=choices)
            else:
                field = Field(label=opt.label,
                              help_text=help_text,
                              required=opt.required)

            f.fields.insert(index, 'option_%s' % opt.id, field)

            index += 1

        if self.captcha and not request.user.is_authenticated():
            captcha_field = custom_fields.CaptchaField(request.META['REMOTE_ADDR'])
            f.fields.insert(index, 'captcha', captcha_field)

        return f


class ContactFormOpt(models.Model):

    __metaclass__ = TransMeta

    label = models.CharField(verbose_name=_('label'), max_length=200)
    field_type = models.CharField(verbose_name=_('type'), max_length=20,
                                choices=FIELD_TYPE_CHOICES)
    help_text = models.TextField(verbose_name=_('help text'), blank=True)
    order = models.IntegerField(verbose_name=_('order'), blank=True,
                                null=True)
    required = models.BooleanField(verbose_name=_('required'))

    contact_form = models.ForeignKey(ContactForm,
                                  verbose_name=_('contact form'),
                                  related_name='opts')

    class Meta:
        translate = ('label', 'help_text')
        verbose_name = _('Configurable field')
        verbose_name_plural = _('Configurable fields')
        ordering = ('order', )

    def __unicode__(self):
        return self.label


class ContactFormSelectOpt(models.Model):

    __metaclass__ = TransMeta

    label = models.CharField(verbose_name=_('label'), max_length=200)
    value = models.CharField(verbose_name=_('value'), max_length=200)
    option = models.ForeignKey(ContactFormOpt,
                               verbose_name=_('select option'),
                               related_name=_('choices'))

    class Meta:
        translate = ('label', )

    def __unicode__(self):
        return self.label


class SentContactForm(models.Model):

    contact_form = models.ForeignKey(ContactForm, verbose_name=_(u'contact form'))
    sender = models.ForeignKey(User, verbose_name=_('sender'), blank=True, null=True)
    sent_msg = JSONField(verbose_name=_(u'response'))
    sent_date = models.DateTimeField(verbose_name=_('sent date'), auto_now_add=True)

    def __unicode__(self):
        return self.contact_form.title
