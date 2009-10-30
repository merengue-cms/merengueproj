# -*- coding: utf-8 -*-
from models import Chunk

from cmsutils.forms.widgets import TinyMCE

from merengue.base.admin import BaseAdmin

replace_dict = {u'á': u'&aacute;', u'é': u'&eacute;', u'í': u'&iacute;', u'ó': u'&oacute;', u'ú': u'&uacute;', u'ñ': '&ntilde;', u'Ñ': '&Ntilde;'}


class TransTinyMCEWidget(TinyMCE):
    '''
    Subclasses TransTextWidget to use TinyMCE visual html editor
    '''

    def __init__(self, *args, **kwargs):
        super(TransTinyMCEWidget, self).__init__(*args, **kwargs)
        self.mce_settings['theme_advanced_buttons1'] = "undo,redo,separator,cut,copy,paste,separator,separator,bold,italic,underline,justifyleft,justifycenter,justifyright,bullist,numlist,outdent,indent"

    def get_input(self, name, value, lang, attrs, id=None):
        field_name = '%s_%s' % (name, lang)
        attrs['id'] = 'id_%s' % field_name
        return TinyMCE.render(self, field_name, value, attrs)


class ChunkAdmin(BaseAdmin):
    list_display = ('key', )
    search_fields = ('key', 'content')

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(ChunkAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name.find('content') == 0:
            field.widget = TransTinyMCEWidget()
        return field

    def get_form(self, request, obj=None):
        form = super(ChunkAdmin, self).get_form(request, obj)

        def clean(self):
            if self.cleaned_data.get('content'):
                for key in self.cleaned_data['content'].keys():
                    self.cleaned_data['content'][key] = ''.join(map(replace, self.cleaned_data['content'][key]))
            return self.cleaned_data

        form.clean = clean
        return form


def register(site):
    """ Merengue admin registration callback """
    site.register(Chunk, ChunkAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Chunk)


def replace(c):
    if c in replace_dict.keys():
        return replace_dict[c]
    else:
        return c
