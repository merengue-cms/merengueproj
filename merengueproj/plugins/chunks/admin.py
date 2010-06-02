# -*- coding: utf-8 -*-
from models import Chunk

from cmsutils.forms.widgets import TinyMCE

from merengue.base.admin import BaseAdmin
from plugins.chunks.forms.forms import ChunkAdminModelForm


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
    form = ChunkAdminModelForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(ChunkAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name.find('content') == 0:
            field.widget = TransTinyMCEWidget()
        return field


def register(site):
    """ Merengue admin registration callback """
    site.register(Chunk, ChunkAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Chunk)
