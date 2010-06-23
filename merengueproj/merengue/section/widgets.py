# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class SearchFormOptionsWidget(forms.Textarea):

    class Media:
        js = (
            '%sjs/search_form_options_widget.js' % settings.MEDIA_URL,
        )

    def __init__(self, attrs={}, search_form_selector_id='id_search_form'):
        self.search_form_selector_id=search_form_selector_id
        attrs.update({'class': 'SearchFormOptionsWidget'})
        super(SearchFormOptionsWidget, self).__init__(attrs)

    def render(self, *args, **kwargs):
        textarea = super(SearchFormOptionsWidget, self).render(*args, **kwargs)
        widget_text = u'%s' % textarea
        widget_text += u'<input type="hidden" name="search_form_selector_id" value="%s" />' % self.search_form_selector_id
        widget_text += u'<img src="%simg/ajax-loader-admin.gif" alt="%s" class="hide SearchFormOptionsWidgetLoading" />' % (settings.MEDIA_URL, _(u'Please wait...'))
        return mark_safe(widget_text)


class CSSValidatorWidget(AdminTextareaWidget):

    def widget_checkbox(self, final_attrs, label, suffix):
        return u'<input type="checkbox" name="%s" id="%s">' \
                    u'<label class="vCheckboxLabel" for="%s">%s</label>' \
                                                                     %('%s%s' %(final_attrs.get('name', ''), suffix),
                                                                      '%s%s' % (final_attrs.get('id', ''), suffix),
                                                                      '%s%s' % (final_attrs.get('id', ''), suffix),
                                                                      label)

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs['style'] = 'display:block'
        textarea = super(CSSValidatorWidget, self).render(name, value, attrs)
        widget_text = u'%s' % textarea
        final_attrs = self.build_attrs(attrs, name=name)
        self.final_attrs = final_attrs
        widget_show_all_errors = self.widget_checkbox(final_attrs, _('Show all errors'), "_show_all_errors")
        widget_normalize = self.widget_checkbox(final_attrs, _('Normalize css'), "_normalize")
        widget_text = u'%s <div class="css-validator-checkboxes"><div>%s</div><div>%s</div></div>' % (widget_text, widget_show_all_errors, widget_normalize)
        return mark_safe(widget_text)
