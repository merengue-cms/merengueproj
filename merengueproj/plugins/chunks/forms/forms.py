# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import get_language

from merengue.base.forms import BaseAdminModelForm
from plugins.chunks.forms import widgets
from plugins.chunks.models import Chunk


replace_dict = {u'á': u'&aacute;', u'é': u'&eacute;', u'í': u'&iacute;', u'ó': u'&oacute;', u'ú': u'&uacute;', u'ñ': '&ntilde;', u'Ñ': '&Ntilde;'}


class ChunkForm(forms.ModelForm):

    class Media:
        js = ('%sjs/tinyimages.js' % settings.MEDIA_URL, )

    class Meta:
        model = Chunk

    def __init__(self, *args, **kwargs):
        super(ChunkForm, self).__init__(*args, **kwargs)
        extra_mce_settings = getattr(settings, 'EXTRA_MCE', {})
        extra_mce_settings.update({'inplace_edit': True,
                              'theme_advanced_buttons1': 'outdent,indent,cut,copy,paste,pastetext,pasteword,preview,code',
                              'theme_advanced_buttons2': 'bold,italic,underline,justifyleft,justifycenter,justifyright,bullist,numlist,link',
                              'theme_advanced_buttons3': 'fontselect,fontsizeselect,',
                              'file_browser_callback': 'CustomFileBrowser',
                             })
        content_language = "content_%s" % get_language()
        self.fields[content_language].widget = widgets.TinyMCEChunk(extra_mce_settings=extra_mce_settings, print_head=False)

    def save(self, current_language, commit=True):
        return super(ChunkForm, self).save(commit)


class ChunkAdminModelForm(BaseAdminModelForm):

    def clean(self):
        if self.cleaned_data.get('content'):
            for key in self.cleaned_data['content'].keys():
                self.cleaned_data['content'][key] = ''.join(map(replace, self.cleaned_data['content'][key]))
        return self.cleaned_data


def replace(c):
    if c in replace_dict.keys():
        return replace_dict[c]
    else:
        return c
