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

# -*- coding: utf-8 -*-
from models import Chunk

from cmsutils.forms.widgets import TinyMCE

from merengue.base.admin import PluginAdmin
from plugins.chunks.forms import ChunkAdminModelForm


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


class ChunkAdmin(PluginAdmin):
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
