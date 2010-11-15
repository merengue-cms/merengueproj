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

if settings.USE_GIS:
    from django.contrib.gis.db import models
else:
    from django.db import models

from django.utils.translation import ugettext_lazy as _

from transmeta import TransMeta

from merengue.base.models import BaseContent


FIELD_TYPE_CHOICES = (
    ('text', _('Text')),
    ('textarea', _('Text araea')),
    ('date', _('Date')),
    ('datetime', _('Datetime')),
    ('checkbox', _('Checkbox')),
    ('select', _('Select')),
)


class ContactFormOpt(models.Model):

    __metaclass__ = TransMeta

    label = models.CharField(verbose_name=_('label'), max_length=200)
    field_type = models.CharField(verbose_name=_('type'), max_length=20,
                                choices=FIELD_TYPE_CHOICES)
    help_text = models.TextField(verbose_name=_('help text'), blank=True)
    order = models.IntegerField(verbose_name=_('order'), blank=True,
                                null=True)

    class Meta:
        translate = ('label', 'help_text')
        verbose_name = _('Configurable field')
        verbose_name_plural = _('Configurable fields')
        ordering = ('order', )

    def __unicode__(self):
        return self.label


class ContactForm(models.Model):

    __metaclass__ = TransMeta

    title = models.CharField(verbose_name=_('name'), max_length=200)
    description = models.TextField(verbose_name=_('description'))
    email = models.EmailField(verbose_name=_('email'),
                              default=settings.DEFAULT_FROM_EMAIL)
    subject = models.CharField(verbose_name=_('subject'), max_length=200)
    subject_fixed = models.BooleanField(verbose_name=_('fixed subject'))
    submit_msg = models.CharField(verbose_name=_('submit'), max_length=200)
    reset_msg = models.CharField(verbose_name=_('reset'), max_length=200,
                                 blank=True)
    reset_button = models.BooleanField(verbose_name=_('reset button'),
                                        default=False)

    content = models.ManyToManyField(BaseContent,
                                     verbose_name=_('content'),
                                     related_name='contact_form',
                                     blank=True, null=True)

    opts = models.ManyToManyField(ContactFormOpt,
                                  verbose_name=_('option'),
                                  related_name='contact_forms',
                                  blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        translate = ('title', 'description', 'subject', 'submit_msg',
                     'reset_msg', )
        verbose_name = _('Contact Form')
        verbose_name_plural = _('Contact Forms')

    def get_form(self, *args, **kwargs):
        from django import forms
        from django.utils.translation import ugettext as _

        class TextAreaField(forms.CharField):
            widget = forms.widgets.Textarea

        fields = {
            'text': forms.CharField,
            'textarea': TextAreaField,
            'date': forms.DateField,
            'datetime': forms.DateTimeField,
            'checkbox': forms.BooleanField,
        }

        f = forms.Form(*args, **kwargs)
        index = 0

        if not self.subject_fixed:
            f.fields.insert(index, 'subject', forms.CharField(label=_('Subject')))
            index += 1

        for opt in self.opts.all():
            Field = fields[opt.field_type]
            help_text = opt.help_text

            # Adding date format to help_text
            if opt.field_type in ['date', 'datetime']:
                help_text += _('<br/>format: (%s)') % Field.widget.format

            f.fields.insert(index, 'option_%s' % opt.id,
                            Field(label=opt.label,
                                  help_text=help_text,
                                  required=False))
            index += 1

        return f
