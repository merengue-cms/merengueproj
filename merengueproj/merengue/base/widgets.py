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

import BeautifulSoup
import datetime
import re

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper, AdminDateWidget
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms.util import flatatt
from django.forms.widgets import DateTimeInput
from django.utils import datetime_safe
from django.utils.encoding import force_unicode, smart_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import ugettext as _

from cmsutils.forms.widgets import TinyMCE, TINYMCE_JS


class ReadOnlyWidget(forms.Widget):

    def __init__(self, original_value, display_value):
        self.original_value = original_value
        self.display_value = display_value

        super(ReadOnlyWidget, self).__init__()

    def render(self, name, value, attrs=None):
        if self.display_value is not None:
            return unicode(self.display_value)
        return unicode(self.original_value)

    def value_from_datadict(self, data, files, name):
        return self.original_value


class CustomTinyMCE(TinyMCE):

    class Media:
        js = (TINYMCE_JS,
              '%smerengue/js/tiny_mce_internal_links/tiny_mce_internal_links.js' % settings.MEDIA_URL,
              #'%stinyimages/js/tiny_mce_file.js' % settings.MEDIA_URL,
              #'%sjs/tiny_mce_iframes/tiny_mce_iframes.js' % settings.MEDIA_URL,
              '%stinyimages/js/tinyimages.js' % settings.MEDIA_URL,
              #'%sjs/tiny_mce_preformatted_text/tiny_mce_preformatted_text.js' % settings.MEDIA_URL,
                )

    def __init__(self, *args, **kwargs):
        super(CustomTinyMCE, self).__init__(*args, **kwargs)
        self.mce_settings['width'] = '50%'
        self.mce_settings['height'] = '200px'
        self.mce_settings['theme_advanced_buttons1'] = "undo,redo,separator,cut,copy,paste,pasteword,separator,bold,italic,underline,separator,justifyleft,justifycenter,justifyright,separator,bullist,numlist,outdent,indent,separator,preformatted_text,tablecontrols"
        self.mce_settings['theme_advanced_buttons2'] = "styleselect,formatselect,fontselect,fontsizeselect,separator,forecolor,link,code,internal_links,iframes,image,file"
        self.mce_settings['theme_advanced_blockformats'] = 'h1,h2,h4,blockquote'
        self.mce_settings['plugins'] = "preview,paste,table,-internal_links,-iframes,-preformatted_text,-file"
        self.mce_settings['plugin_internal_links_base_url'] = '%smerengue/js/tiny_mce_internal_links/' % settings.MEDIA_URL
        try:
            self.mce_settings['plugin_internal_links_url'] = reverse('internal_links_search')
        except NoReverseMatch:
            pass
        self.mce_settings['plugin_iframes_url'] = "/iframes/"
        self.mce_settings['plugin_file_url'] = "/tinyimages/file_upload/"
        self.mce_settings['file_browser_callback'] = "TinyImagesFileBrowser"
        try:
            self.mce_settings['tiny_images_base_url'] = reverse('tinyimage_list') + '../'
        except NoReverseMatch:
            pass
        self.mce_settings['urlconverter_callback'] = "customUrlConverter"
        content_css = settings.TINYMCE_EXTRA_MEDIA.get('css', [])
        content_js = settings.TINYMCE_EXTRA_MEDIA.get('css', [])
        content_css.extend(["merengue/css/editorstyles.css"])
        content_css = ','.join(["%s%s" % (settings.MEDIA_URL, css) for css in content_css])
        self.mce_settings['content_css'] = content_css
        self.mce_settings['content_js'] = content_js
        self.mce_settings['extended_valid_elements'] = "hr[class|width|size|noshade],font[face|size|color|style],iframe[src|width|height|id|class|frameborder|border|marginwidth|marginheight|leftmargin|topmargin|allowtransparency|style],span[class|align|style],-table[border=0|cellspacing|cellpadding|width|height|class|align|summary|style|dir|id|lang|bgcolor|background|bordercolor],-tr[id|lang|dir|class|rowspan|width|height|align|valign|style|bgcolor|background|bordercolor],tbody[id|class],thead[id|class],tfoot[id|class],-td[id|lang|dir|class|colspan|rowspan|width|height|align|valign|style|bgcolor|background|bordercolor|scope],-th[id|lang|dir|class|colspan|rowspan|width|height|align|valign|style|scope],caption[id|lang|dir|class|style]"

    def render(self, name, value, attrs=None):
        urlconverter_callback = """<script type="text/javascript">
        function customUrlConverter(url, node, on_save) { return url; }
        </script>"""
        result = super(CustomTinyMCE, self).render(name, value, attrs)
        return mark_safe(u'%s%s' % (urlconverter_callback, result))

    def value_from_datadict(self, data, files, name):
        value = super(CustomTinyMCE, self).value_from_datadict(data, files, name)
        soup = BeautifulSoup.BeautifulSoup(value)
        allowed_attrs_valid_elemments = []
        if 'extended_valid_elements' in self.mce_settings:
            pattern = re.compile(r'\w*\[(?P<attrs>[\||\w]+)\]\w*')

            def add_attrs_valid_elements(match):
                attrs = match.group('attrs').split('|')
                allowed_attrs_valid_elemments.extend(attrs)
            pattern.sub(add_attrs_valid_elements, self.mce_settings['extended_valid_elements'])
        allowed_attrs = ('type', 'name', 'id', 'value', 'border', 'hspace', 'vspace', 'target', 'href', 'mce_href', '_moz_dirty') + \
                        tuple(set(allowed_attrs_valid_elemments))
        unallowed_tags = ('font', 'color', )
        forbidden_tags = ('style', 'link', 'meta', 'script', 'xml', )
        for tag in soup.findAll():
            if tag.name in forbidden_tags:
                tag.hidden=True
            elif tag.name in unallowed_tags:
                tag.name = 'span'
            else:
                attr_todel=[]
                for at, val in tag.attrs:
                    if at not in allowed_attrs:
                        attr_todel.append(at)
                for at in attr_todel:
                    del(tag[at])

        for posible_comment in soup.findAll(text=re.compile('\[if')):
            if isinstance(posible_comment, BeautifulSoup.Comment):
                posible_comment.extract()

        return unicode(soup).strip()


class RelatedFieldWidgetWrapperWithoutAdding(RelatedFieldWidgetWrapper):

    def render(self, name, value, *args, **kwargs):
        return self.widget.render(name, value, *args, **kwargs)


class AdminDateOfDateTimeWidget(AdminDateWidget):

    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.datetime):
            value = value.date()
        return super(AdminDateOfDateTimeWidget, self).render(name, value, attrs)


class TranslatableInputDateWidget(DateTimeInput):

    class Media:
        js = ('/jsi18n/',
              '%smerengue/js/dates_l10n/dates_l10n.js' % settings.MEDIA_URL,
              '%sjs/core.js' % settings.ADMIN_MEDIA_PREFIX,
              '%sjs/calendar.js' % settings.ADMIN_MEDIA_PREFIX,
              '%smerengue/js/DateTimeShortcuts.js' % settings.MEDIA_URL,
                )

        css = {'all': ('%smerengue/css/event_calendar.css' % settings.MEDIA_URL, )}

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif hasattr(value, 'strftime'):
            value = datetime_safe.new_datetime(value)
            value = value.strftime(self.format)
        hidden_final_attrs = self.build_attrs(attrs, type='hidden', name=name)
        final_attrs = self.build_attrs(attrs, type=self.input_type, name='visual-'+name)
        final_attrs.update({'id': 'visual-' + final_attrs.get('id', name)})
        final_attrs.update({'class': 'vDateField TranslatableInputDateWidget'})
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            hidden_final_attrs['value'] = force_unicode(value)
        jsdates = '<script type="text/javascript" src="%smerengue/js/dates_l10n/dates_l10n_%s.js"></script>' % (settings.MEDIA_URL, get_language())
        jsdates = '<script type="text/javascript" src="%smerengue/js/translatable_input_date_widget.js"></script>' % settings.MEDIA_URL
        return mark_safe(u'%s<input%s /><input%s />' % (jsdates, flatatt(final_attrs), flatatt(hidden_final_attrs)))


class InputTimeWidget(forms.TextInput):

    class Media:
        js = (settings.ADMIN_MEDIA_PREFIX + "js/calendar.js",
              '%smerengue/js/DateTimeShortcuts.js' % settings.MEDIA_URL)

    def __init__(self, attrs={}):
        super(InputTimeWidget, self).__init__(attrs={'class': 'vTimeField', 'size': '8'})


class TranslatableSplitDateTimeWidget(forms.SplitDateTimeWidget):
    """
    TranslatableSplitDateTimeWidget widget
    """

    def __init__(self, attrs=None):
        widgets = [TranslatableInputDateWidget, InputTimeWidget]
        forms.MultiWidget.__init__(self, widgets, attrs)

    def format_output(self, rendered_widgets):
        return mark_safe(u'<p class="datetime">%s %s<br />%s %s</p>' % \
            (_('Date:'), rendered_widgets[0], _('Time:'), rendered_widgets[1]))


class RelatedBaseContentWidget(RelatedFieldWidgetWrapper):

    class Media:
        js = ('%smerengue/js/jquery.basecontentwidget.js' % settings.MEDIA_URL, )

    def __init__(self, *args, **kwargs):
        self.hide_original_widget = kwargs.pop('hide_original_widget', True)
        super(RelatedBaseContentWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, *args, **kwargs):
        output = u'<div style="float: left;" class="RelatedBaseContentWidget">'
        if self.hide_original_widget:
            output += u'<div style="padding-top: 3px; font-size:12px; line-height: 16px;">'
            output += u'<span class="selected_content">'
            output += smart_unicode(value)
            output += u'</span>'
            output += u'<span class="remove_current" style="display: none; margin: 0px 1em;">'
            output += u'<img style="cursor: pointer;" src="%(media)smerengue/img/admin/cancel.png" alt="%(title)s" title="%(title)s" />' % {
                'title': _(u'Remove'),
                'media': settings.MEDIA_URL}
            output += u'</span>'
            output += u'</div>'
            output += u'<div style="display: none;">'
            output += super(RelatedBaseContentWidget, self).render(name, value, *args, **kwargs)
            output += u'</div>'
        else:
            output += super(RelatedBaseContentWidget, self).render(name, value, *args, **kwargs)
            output += u'<br />'
        params=[]
        if getattr(self.widget, 'choices', None):
            for id, value in self.widget.choices:
                if not isinstance(id, int):
                    continue
                params.append(str(id))
        if params:
            params_str = '&id__in=%s' % ','.join(params)
        else:
            params_str = ''

        output += u'<a id="lookup_id_%s" href="/admin/base/basecontent/?for_select=1%s" onclick="javascript:showRelatedObjectLookupPopup(this); return false;">%s</a>' % (name, params_str, _('Select content'))
        output += u'</div>'
        output += u'<br style="clear: left;" />'
        return mark_safe(u''.join(output))

if settings.USE_GIS:
    from django.contrib.gis.admin.widgets import OpenLayersWidget
    from django.contrib.gis.geos import GEOSGeometry, GEOSException

    class OpenLayersWidgetLatitudeLongitude(OpenLayersWidget):

        def render(self, name, value, attrs):
            html = super(OpenLayersWidgetLatitudeLongitude, self).render(name, value, attrs)
            # If a string reaches here (via a validation error on another
            # field) then just reconstruct the Geometry.
            if isinstance(value, basestring):
                try:
                    value = GEOSGeometry(value)
                except (GEOSException, ValueError):
                    value = None

            if value and value.geom_type.upper() != self.geom_type:
                value = None

            geom_type = self.params['geom_type']
            if geom_type.name == 'Point':
                value_latitude = (value and value.get_y()) or ''
                value_longitude = (value and value.get_x()) or ''
                latitude = self._emule_widget_django('latitude', 'latitude', name, value_latitude)
                longitude = self._emule_widget_django('longitude', 'longitude', name, value_longitude)
                view_on_map = "<input id='view_on_map_%s' class='view_on_map' type='button' value='%s'/>" % (name, _('View on map'))
                return mark_safe("%s %s %s %s"% (html, latitude, longitude, view_on_map))
            return html

        def _emule_widget_django(self, label, sufix, name, value):
            label = _(label)
            _id = "%s_%s" %(name, sufix)
            _str = """<div class='form-row %s'>
                <div>
                    <label for='id_%s'>%s:</label>
                    <input id='id_%s' class='change_%s' type='text' name='%s' value='%s'/>
                </div>
            </div>"""%(name, _id, label, _id, sufix, _id, value)
            return _str

    class OpenLayersInlineAwareWidget(OpenLayersWidget):

        def render(self, name, value, attrs=None):
            self.params.update({'widget_name': name})
            return super(OpenLayersInlineAwareWidget, self).render(name, value, attrs)

    class OpenLayersInlineLatitudeLongitude(OpenLayersWidgetLatitudeLongitude):

        def render(self, name, value, attrs=None):
            self.params.update({'widget_name': name})
            return super(OpenLayersInlineLatitudeLongitude, self).render(name, value, attrs)
