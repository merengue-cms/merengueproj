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

from django.conf import settings
from django.utils.encoding import smart_unicode
from django.forms.util import flatatt
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.simplejson import JSONEncoder

from cmsutils.forms.widgets import TinyMCE, load_javascript

TINYMCE_JS = settings.MEDIA_URL + "chunks/js/widgets/tiny_mce/tiny_mce.js"


class TinyMCEChunk(TinyMCE):

    def __init__(self, extra_mce_settings={}, print_head=False, *args, **kwargs):
        super(TinyMCEChunk, self).__init__(extra_mce_settings, print_head, *args, **kwargs)
        self.mce_settings["height"] = "100%"
        self.mce_settings["auto_height"] = True
        self.mce_settings["convert_on_click"] = True

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        value = smart_unicode(value)
        final_attrs = self.build_attrs(attrs, name=name)

        self.mce_settings['elements'] = "id_%s" % name
        mce_json = JSONEncoder().encode(self.mce_settings)

        # Print script head once per instance
        if self.print_head:
            head = load_javascript(TINYMCE_JS)
        else:
            head = u''

        return mark_safe(u'''<textarea%(attrs)s>%(content)s</textarea>
                %(head)s
                <script type="text/javascript">
                    var field_name = "%(field_name)s";
                    tinyMCE.init(%(mce_settings)s);
                    jQuery("#view_%(field_name)s").dblclick(function () {
                        var tools = jQuery(this).next('.inplace-tools');
                        var textarea = tools.find("#id_%(field_name)s");
                        var editor_id = tinyMCE.idCounter;
                        tinyMCE.addMCEControl(textarea[0], textarea[0].id);
                        jQuery("#tools_%(field_name)s_cancel_id").click(function () {
                            tinyMCE.removeMCEControl("mce_editor_" + editor_id);
                        });
                        jQuery("#tools_%(field_name)s_apply_id").click(function () {
                            document.getElementById('tools_%(field_name)s').style.display = 'none';
                            tinyMCE.removeMCEControl("mce_editor_" + editor_id);
                        });
                    });
                </script>''' % {'attrs': flatatt(final_attrs),
                                'content': escape(value),
                                'head': head,
                                'field_name': name,
                                'mce_settings': mce_json})
