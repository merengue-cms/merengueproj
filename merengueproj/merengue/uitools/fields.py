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

from inplaceeditform.fields import AdaptorTextAreaField, AdaptorImageField
from cmsutils.forms.widgets import TinyMCE

from merengue.base.models import BaseContent, BaseCategory
from merengue.section.models import Menu
from merengue.perms.utils import has_permission


class AdaptorEditInline(object):

    @classmethod
    def can_edit(cls, field):
        request = field.request
        obj = field.obj
        can_edit = False
        edit_permission = 'edit'
        if request.user.is_anonymous():
            pass
        elif request.user.is_superuser:
            can_edit = True
        else:
            if not getattr(request, 'cache_edit_inline', None):
                request.cache_edit_inline = {}
            if not isinstance(obj, BaseContent):
                if isinstance(obj, BaseCategory):
                    edit_permission = 'manage_category'
                if isinstance(obj, Menu):
                    obj = obj.get_section()
                else:
                    obj = None
            if obj in request.cache_edit_inline:
                can_edit = request.cache_edit_inline.get(obj)
            else:
                can_edit = has_permission(obj, request.user, edit_permission)
            request.cache_edit_inline[obj] = can_edit
        return can_edit


class AdaptorImageThumbnailField(AdaptorImageField):

    def render_value(self, field_name=None, template_name='adaptor_imagethumbnail/render_value.html'):
        return super(AdaptorImageThumbnailField, self).render_value(field_name=field_name, template_name=template_name)


class AdaptorTinyMCEField(AdaptorTextAreaField):

    @property
    def name(self):
        return 'textarea'

    def __init__(self, *args, **kwargs):
        super(AdaptorTinyMCEField, self).__init__(*args, **kwargs)
        self.widget_options = self.config and self.config.get('widget_options', {})

    def get_field(self):
        field = super(AdaptorTinyMCEField, self).get_field()

        tiny_mce_buttons = {
            '0': ['bold', 'italic', 'underline', 'justifyleft',
                  'justifycenter', 'justifyright', 'justifyfull'],
            '1': ['bullist', 'numlist', 'outdent', 'indent'],
            '2': ['undo', 'redo'],
            '3': ['cut', 'copy', 'paste', 'pasteword'],
            '4': ['forecolor', 'link', 'code', 'internal_links'],
            '5': ['iframes', 'image', 'file', 'removeformat'],
            }

        tiny_mce_selectors = {'0': ['fontsizeselect'],
                              '1': ['formatselect', 'fontselect'],
                              '2': ['styleselect']}

        extra_mce_settings = getattr(settings, 'EXTRA_MCE', {})
        extra_mce_settings.update(self._order_tinymce_buttons(tiny_mce_buttons, tiny_mce_selectors))
        content_css = [i for i in settings.TINYMCE_EXTRA_MEDIA.get('css', [])]
        content_js = [i for i in settings.TINYMCE_EXTRA_MEDIA.get('css', [])]
        content_css.extend(["merengue/css/editorstyles.css"])
        content_css = ','.join(["%s%s" % (settings.MEDIA_URL, css) for css in content_css])
        extra_mce_settings.update({'inplace_edit': True,
                              'theme_advanced_blockformats': 'h1,h2,h4,blockquote',
                              'file_browser_callback': 'CustomFileBrowser',
                              'theme_advanced_statusbar_location': "bottom",
                              'theme_advanced_resizing': True,
                              'theme_advanced_resize_horizontal': True,
                              'convert_on_click': True,
                              'content_css': content_css,
                              'content_js': content_js,
                             })
        extra_mce_settings.update(self.widget_options)
        field.field.widget = TinyMCE(extra_mce_settings=extra_mce_settings,
                                           print_head=False)
        return field

    def render_value_edit(self):
        value = super(AdaptorTinyMCEField, self).render_value()
        return render_to_string('tiny_adaptor/render_value.html', {'value': value,
                                                                   'MEDIA_URL': settings.MEDIA_URL,
                                                                   'adaptor': self,
                                                                   'is_ajax': self.request.is_ajax()})

    def render_media_field(self, template_name="tiny_adaptor/render_media_field.html"):
        return super(AdaptorTinyMCEField, self).render_media_field(template_name)

    def _order_tinymce_buttons(self, buttons_priorized, selectors_priorized,
                               button_width=20, selector_width=80):

        result = {
            'theme_advanced_buttons1': '',
            'theme_advanced_buttons2': '',
            'theme_advanced_buttons3': '',
            }
        if not 'width' in self.widget_options or not self.widget_options['width']:
            return result

        total_width = int(self.widget_options['width'].replace('px', ''))
        buttons, selectors = self._priorize_tinymce_buttons(buttons_priorized,
                                                            selectors_priorized,
                                                            button_width,
                                                            selector_width)
        buttons_width = len(buttons) * button_width
        selectors_width = len(selectors) * selector_width

        if total_width >= buttons_width + selectors_width:  # one row
            if total_width >= selectors_width:
                result['theme_advanced_buttons1'] = ','.join(buttons)
                result['theme_advanced_buttons2'] = ','.join(selectors)
            else:
                num_selectors = (total_width - buttons_width) / selector_width
                result['theme_advanced_buttons1'] = ','.join(selectors[:num_selectors] + buttons)

        elif total_width * 2 >= buttons_width + selectors_width:  # two rows
            aux_index = total_width / button_width
            if total_width >= buttons_width:
                result['theme_advanced_buttons1'] = ','.join(buttons)
                result['theme_advanced_buttons2'] = ','.join(selectors)
            else:
                result['theme_advanced_buttons1'] = ','.join(buttons[:aux_index])
                result['theme_advanced_buttons2'] = ','.join(selectors + buttons[aux_index:])

        else:
            aux_index = total_width / button_width
            result['theme_advanced_buttons1'] = ','.join(buttons[:aux_index])
            result['theme_advanced_buttons2'] = ','.join(buttons[aux_index:])
            num_selectors = total_width / selector_width
            result['theme_advanced_buttons3'] = ','.join(selectors[:num_selectors])

        return result

    def _priorize_tinymce_buttons(self, buttons, selectors, button_width=20, selector_width=80):
        row_width = int(self.widget_options['width'].replace('px', ''))
        total_width = row_width * 3
        used_width = 0

        buttons_list = []
        selectors_list = []
        # we assume that we have more priority levels on buttons

        for key in buttons:
            if (used_width + button_width * len(buttons[key])) < total_width:
                buttons_list += buttons[key]
                used_width += button_width * len(buttons[key])
            if key in selectors:
                if (used_width + selector_width * len(selectors[key])) < total_width:
                    selectors_list += selectors[key]
                    used_width += selector_width * len(selectors[key])

        return buttons_list, selectors_list
