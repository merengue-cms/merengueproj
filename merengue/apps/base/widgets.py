import BeautifulSoup
import datetime
import re

from django.conf import settings
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper, AdminDateWidget
from django.contrib.gis.admin.widgets import OpenLayersWidget
from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.forms.util import flatatt
from django.forms.widgets import DateTimeInput
from django.utils import datetime_safe
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import ugettext as _

from cmsutils.forms.widgets import TinyMCE, TINYMCE_JS


class CustomTinyMCE(TinyMCE):

    class Media:
        js = (TINYMCE_JS,
              '%sjs/tiny_mce_internal_links/tiny_mce_internal_links.js' % settings.MEDIA_URL,
              '%stinyimages/js/tiny_mce_file.js' % settings.MEDIA_URL,
              '%sjs/tiny_mce_iframes/tiny_mce_iframes.js' % settings.MEDIA_URL,
              '%stinyimages/js/tinyimages.js' % settings.MEDIA_URL,
              '%sjs/tiny_mce_preformatted_text/tiny_mce_preformatted_text.js' % settings.MEDIA_URL,
                )

    def __init__(self, *args, **kwargs):
        super(CustomTinyMCE, self).__init__(*args, **kwargs)
        self.mce_settings['width'] = '50%'
        self.mce_settings['height'] = '200px'
        self.mce_settings['theme_advanced_buttons1'] = "undo,redo,separator,cut,copy,paste,pasteword,separator,bold,italic,underline,separator,justifyleft,justifycenter,justifyright,separator,bullist,numlist,outdent,indent,separator,preformatted_text,tablecontrols"
        self.mce_settings['theme_advanced_buttons2'] = "styleselect,formatselect,fontselect,fontsizeselect,separator,forecolor,link,code,internal_links,iframes,image,file"
        self.mce_settings['theme_advanced_blockformats'] = 'h1,h2,h4,blockquote'
        self.mce_settings['plugins'] = "preview,paste,table,-internal_links,-iframes,-preformatted_text,-file"
        self.mce_settings['plugin_internal_links_url'] = "/internal-links/"
        self.mce_settings['plugin_iframes_url'] = "/iframes/"
        self.mce_settings['plugin_file_url'] = "/tinyimages/file_upload/"
        self.mce_settings['file_browser_callback'] = "TinyImagesFileBrowser"
        self.mce_settings['urlconverter_callback'] = "customUrlConverter"
        self.mce_settings['content_css'] = "/media/css/editorstyles.css"
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


class AdminDateOfDateTimeWidget(AdminDateWidget):

    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.datetime):
            value = value.date()
        return super(AdminDateOfDateTimeWidget, self).render(name, value, attrs)


class TranslatableInputDateWidget(DateTimeInput):

    class Media:
        js = ('/jsi18n/',
              '%sjs/dates_l10n/dates_l10n.js' % settings.MEDIA_URL,
              '%sjs/core.js' % settings.ADMIN_MEDIA_PREFIX,
              '%sjs/calendar.js' % settings.ADMIN_MEDIA_PREFIX,
              '%sjs/DateTimeShortcuts.js' % settings.MEDIA_URL,
                )

        css = {'all': ('%scss/event_calendar.css' % settings.MEDIA_URL, )}

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
        jsdates = '<script type="text/javascript" src="%sjs/dates_l10n/dates_l10n_%s.js"></script>' % (settings.MEDIA_URL, get_language())
        jsdates += '<script type="text/javascript" src="%sjs/translatable_input_date_widget.js"></script>' % settings.MEDIA_URL
        return mark_safe(u'%s<input%s /><input%s />' % (jsdates, flatatt(final_attrs), flatatt(hidden_final_attrs)))
