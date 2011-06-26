# Copyright (c) 2010 by Yaco Sistemas
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

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.forms import BoundField
from django.forms.models import save_instance
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.text import capfirst
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from genericforeignkey.forms import GenericAdminModelForm
from transmeta import canonical_fieldname

from notification import models as notification
from announcements.forms import AnnouncementAdminForm as AnnouncementAdminDefaultForm
from threadedcomments.models import FreeThreadedComment
from threadedcomments.forms import FreeThreadedCommentForm
from captcha.fields import CaptchaField


def _get_fieldsets(self):
    if not self.fieldsets:
        yield dict(name=None, fields=self)
    else:
        for fieldset, fields in self.fieldsets:
            fieldset_dict = dict(name=fieldset, fields=[])
            for field_name in fields:
                if field_name in self.fields.keyOrder:
                    fieldset_dict['fields'].append(self[field_name])
            if not fieldset_dict['fields']:
                # if there is no fields in this fieldset,
                # we continue to next fieldset
                continue
            yield fieldset_dict


def _get_tabs(self):
    if not self.tabs:
        yield dict(name=None, fields=self)
    else:
        for tab, fieldsets in self.tabs:
            tabs_dict = dict(name=tab, fieldsets=[])
            for fieldset, fields in fieldsets:
                fieldset_dict = dict(name=fieldset, fields=[])
                for field_name in fields:
                    if field_name in self.fields.keyOrder:
                        fieldset_dict['fields'].append(self[field_name])
                if not fieldset_dict['fields']:
                    # if there is no fields in this fieldset,
                    # we continue to next fieldset
                    continue
                tabs_dict['fieldsets'].append(fieldset_dict)
            yield tabs_dict


def _as_div(self):
    "Returns this form rendered as HTML <div>s."
    return render_to_string('base/baseform.html', {'form': self})


class FormAdminDjango(object):
    """
    Abstract class implemented to provide form django admin like
    Usage::

       class FooForm(forms.Form, FormAdminDjango):
          ...
    """

    def as_django_admin(self):
        return render_to_string(
            'base/form_admin_django.html',
            {'form': self, },
        )


class FormRequiredFields(object):

    required_css_class = 'required'

    def as_table_required(self):
        """
        Returns form rendered as HTML <tr>s -- excluding the <table></table>.
        """
        return self._html_output_required(
            normal_row=u'<tr%(html_class_attr)s><th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td></tr>',
            error_row=u'<tr><td colspan="2">%s</td></tr>',
            row_ender=u'</td></tr>',
            help_text_html=u'<br /><span class="helpText">%s</span>',
            errors_on_separate_row=False)

    def as_ul_required(self):
        """
        Returns form rendered as HTML <li>s -- excluding the <ul></ul>.
        """
        return self._html_output_required(
            normal_row=u'<li%(html_class_attr)s>%(errors)s%(label)s %(field)s%(help_text)s</li>',
            error_row=u'<li>%s</li>',
            row_ender='</li>',
            help_text_html=u'<span class="helpText">%s</span>',
            errors_on_separate_row=False)

    def as_p_required(self):
        """
        Returns this form rendered as HTML <p>s.
        """
        return self._html_output_required(
            normal_row=u'<p%(html_class_attr)s>%(label)s %(field)s%(help_text)s</p>',
            error_row=u'%s',
            row_ender='</p>',
            help_text_html=u'<span class="helpText">%s</span>',
            errors_on_separate_row=True)

    def css_classes(self, extra_classes=None):
        """
        Returns a string of space-separated CSS classes for this field.
        """
        if hasattr(extra_classes, 'split'):
            extra_classes = extra_classes.split()
        extra_classes = set(extra_classes or [])
        if self.errors and hasattr(self.form, 'error_css_class'):
            extra_classes.add(self.form.error_css_class)
        if self.field.required and hasattr(self.form, 'required_css_class'):
            extra_classes.add(self.form.required_css_class)
        return ' '.join(extra_classes)

    def _html_output_required(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        """
        Helper function for outputting HTML. Used by as_table(), as_ul(), as_p().
        """
        top_errors = self.non_field_errors()  # Errors that should be displayed above all fields.
        output, hidden_fields = [], []

        for name, field in self.fields.items():
            html_class_attr = ''
            bf = BoundField(self, field, name)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors])  # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                # Create a 'class="..."' atribute if the row should have any
                # CSS classes applied.
                html_class_attr = ''
                field_classes = []
                if field.required:
                    field_classes.append(self.required_css_class)
                if bf_errors:
                    field_classes.append('error')
                if field_classes:
                    html_class_attr = ' class="%s"' % " ".join(field_classes)

                if errors_on_separate_row and bf_errors:
                    output.append(error_row % force_unicode(bf_errors))

                if bf.label:
                    label = conditional_escape(force_unicode(bf.label))
                    # Only add the suffix if the label does not end in
                    # punctuation.
                    if self.label_suffix:
                        if label[-1] not in ':?.!':
                            label += self.label_suffix
                    label = bf.label_tag(label) or ''
                else:
                    label = ''

                if field.help_text:
                    help_text = help_text_html % force_unicode(field.help_text)
                else:
                    help_text = u''

                output.append(normal_row % {
                    'errors': force_unicode(bf_errors),
                    'label': force_unicode(label),
                    'field': unicode(bf),
                    'help_text': help_text,
                    'html_class_attr': html_class_attr,
                })

        if top_errors:
            output.insert(0, error_row % force_unicode(top_errors))

        if hidden_fields:  # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                if not last_row.endswith(row_ender):
                    # This can happen in the as_p() case (and possibly others
                    # that users write): if there are only top errors, we may
                    # not be able to conscript the last row for our purposes,
                    # so insert a new, empty row.
                    last_row = (normal_row % {'errors': '', 'label': '',
                                              'field': '', 'help_text': '',
                                              'html_class_attr': html_class_attr})
                    output.append(last_row)
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe(u'\n'.join(output))


class FormTabs(object):
    """
    Abstract class implemented to provide form with tabs like
    Usage::

       class FooForm(forms.Form, FormTabs):
          tabs = (
                  ({'name': _(tab1_name), 'title': _(tab1_title)}, (
                        (_(accordion1),
                            (fiel1d, field2, ... )),
                        (_(accordion2), ...)
                    ),
                ),
                ...
            )
    """
    tabs = ()
    get_tabs = property(_get_tabs)

    class Media:
        js = (
              settings.MEDIA_URL + "merengue/js/formtabs/formtabs_initial.js",
             )
        css = {'all': (settings.MEDIA_URL + "merengue/css/formtabs/ui-lightness/ui.all.css",
                      )}

    def as_tab(self):
        return render_to_string('base/formtabs.html', {'form': self, })


class BaseForm(forms.Form, FormRequiredFields):
    fieldsets = ()
    two_columns_fields = ()
    three_columns_fields = ()
    get_fieldsets = property(_get_fieldsets)

    def __unicode__(self):
        return self.as_div()

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.two_columns_fields:
                field.column_style = 'twoColumnsField'
            elif name in self.three_columns_fields:
                field.column_style = 'threeColumnsField'

    as_div = _as_div


class BaseModelForm(forms.ModelForm, FormAdminDjango, FormRequiredFields):
    fieldsets = ()
    two_columns_fields = ()
    three_columns_fields = ()
    get_fieldsets = property(_get_fieldsets)

    def _add_transmeta_fields(self, instance):
        opts = self._meta
        lang = get_language()
        if opts.model:
            field_list = []
            modelopts = opts.model._meta
            transmeta_fields = [f for f in modelopts.fields if canonical_fieldname(f) != f.name]
            for f in transmeta_fields:
                if not f.editable:
                    continue
                if opts.fields and not canonical_fieldname(f) in opts.fields:
                    continue
                if opts.exclude and canonical_fieldname(f) in opts.exclude:
                    continue
                if not f.name.endswith('_' + lang):
                    continue
                formfield = f.formfield()
                formfield.label = capfirst(_(canonical_fieldname(f)))
                formfield.lang_name = f.name
                if instance and not canonical_fieldname(f) in self.initial.keys():
                    self.initial.update({canonical_fieldname(f): f.value_from_object(instance)})
                if formfield:
                    field_list.append((canonical_fieldname(f), formfield))
            self.transmeta_fields = SortedDict(field_list)
            self.fields.update(self.transmeta_fields)
            if opts.fields:
                order = [fieldname for fieldname in opts.fields if fieldname in self.fields.keys()]
                self.fields.keyOrder = order

    def clean(self):
        cleaned_data = super(BaseModelForm, self).clean()
        if cleaned_data:
            for name, f in self.transmeta_fields.items():
                if name in cleaned_data.keys():
                    cleaned_data.update({f.lang_name: cleaned_data.get(name)})
        return cleaned_data

    def save(self, commit=True):
        if self.instance.pk is None:
            fail_message = 'created'
        else:
            fail_message = 'changed'
        transmeta_field_names = [f.lang_name for f in self.transmeta_fields.values()]
        default_fields = (self._meta.fields and list(self._meta.fields)) or []
        return save_instance(self, self.instance, default_fields + transmeta_field_names, fail_message, commit)

    def __init__(self, *args, **kwargs):
        super(BaseModelForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        self._add_transmeta_fields(instance)
        for name, field in self.fields.items():
            if name in self.two_columns_fields:
                field.column_style = 'twoColumnsField'
            elif name in self.three_columns_fields:
                field.column_style = 'threeColumnsField'

    def __unicode__(self):
        return self.as_p_required()


class CaptchaFreeThreadedCommentForm(BaseModelForm, FreeThreadedCommentForm):

    class Meta:
        model = FreeThreadedComment
        fields = ('comment', 'name', 'website', 'email', )

    def __init__(self, user, *args, **kwargs):
        super(CaptchaFreeThreadedCommentForm, self).__init__(*args, **kwargs)
        if user.is_anonymous():
            captcha_field = CaptchaField()
            self.fields['captcha'] = captcha_field
            self.declared_fields['captcha'] = captcha_field


class AdminBaseContentOwnersForm(forms.Form):

    owners = forms.ModelMultipleChoiceField(User.objects.all(), widget=FilteredSelectMultiple(_('owners'), False))

    class Media:
        js = ('/%s/jsi18n/' % settings.MERENGUE_URLS_PREFIX,
              settings.ADMIN_MEDIA_PREFIX + "js/core.js",
              settings.ADMIN_MEDIA_PREFIX + "js/SelectBox.js",
              settings.ADMIN_MEDIA_PREFIX + "js/SelectFilter2.js",
             )
        css = {'all': (settings.ADMIN_MEDIA_PREFIX + "css/forms.css",
                       settings.MEDIA_URL + "css/admin.css",
                      )}


class BaseAdminModelForm(GenericAdminModelForm):
    pass


class AnnouncementAdminForm(AnnouncementAdminDefaultForm):

    def save(self, commit=True):
        # get announcement object avoiding being sent by the parent
        send = self.cleaned_data["send_now"]
        self.cleaned_data["send_now"] = False
        announcement = super(AnnouncementAdminForm, self).save(commit)

        if send:
            users = User.objects.all()
            notification.send(users, "announcement", {
                "announcement": announcement,
            }, on_site=False, queue=False)
        return announcement
