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

from south.db import db
from django.db import models
from merengue.viewlet.models import *


class Migration:

    def forwards(self, orm):
        # Adding model 'RegisteredViewlet'
        db.create_table('viewlet_registeredviewlet', (
            ('registereditem_ptr', orm['viewlet.RegisteredViewlet:registereditem_ptr']),
            ('name', orm['viewlet.RegisteredViewlet:name']),
        ))
        db.send_create_signal('viewlet', ['RegisteredViewlet'])

    def backwards(self, orm):
        # Deleting model 'RegisteredViewlet'
        db.delete_table('viewlet_registeredviewlet')

    models = {
        'registry.registereditem': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'config': ('merengue.registry.dbfields.ConfigField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'viewlet.registeredviewlet': {
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registereditem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['registry.RegisteredItem']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['viewlet']
