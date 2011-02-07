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
from django.template.loader import render_to_string

from inplaceeditform.fields import AdaptorTextAreaField
from cmsutils.forms.widgets import TinyMCE


class AdaptorTinyMCEField(AdaptorTextAreaField):

    @property
    def name(self):
        return 'textarea'

    def get_field(self):
        field = super(AdaptorTinyMCEField, self).get_field()
        extra_mce_settings = getattr(settings, 'EXTRA_MCE', {})
        extra_mce_settings.update({'inplace_edit': True,
                              'theme_advanced_buttons1': 'outdent,indent,cut,copy,paste,pastetext,pasteword,preview,code',
                              'theme_advanced_buttons2': 'bold,italic,underline,justifyleft,justifycenter,justifyright,bullist,numlist,link',
                              'theme_advanced_buttons3': 'fontselect,fontsizeselect,',
                              'file_browser_callback': 'CustomFileBrowser',
                              'theme_advanced_statusbar_location': "bottom",
                              'theme_advanced_resizing': True,
                              'theme_advanced_resize_horizontal': True,
                              'convert_on_click': True,
                             })
        extra_mce_settings.update(self.options)
        field.field.widget = TinyMCE(extra_mce_settings=extra_mce_settings,
                                           print_head=False)
        return field

    def render_value(self):
        value = super(AdaptorTinyMCEField, self).render_value()
        return render_to_string('tiny_adaptor/render_value.html', {'value': value,
                                                                   'MEDIA_URL': settings.MEDIA_URL,
                                                                   'adaptor': self,
                                                                   'is_ajax': self.request.is_ajax()})

    def render_media_field(self, template_name="tiny_adaptor/render_media_field.html"):
        return super(AdaptorTinyMCEField, self).render_media_field(template_name)
