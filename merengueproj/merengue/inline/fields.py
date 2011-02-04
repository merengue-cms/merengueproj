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
                                                                   'adaptor': self})

    def render_media_field(self, template_name="tiny_adaptor/render_media_field.html"):
        return super(AdaptorTinyMCEField, self).render_media_field(template_name)
