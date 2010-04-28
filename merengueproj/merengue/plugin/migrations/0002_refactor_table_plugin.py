# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."


    def backwards(self, orm):
        "Write your backwards methods here."
        #for p in orm['plugin.registeredplugin'].objects.all():
        #    p.module = p.module.replace('plugins.', 'plugin.'


    models = {
        'plugin.registeredplugin': {
            'Meta': {'object_name': 'RegisteredPlugin', 'db_table': "'plugins_registeredplugin'", '_ormbases': ['registry.RegisteredItem']},
            'description': ('django.db.models.fields.TextField', [], {}),
            'directory_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'installed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registereditem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['registry.RegisteredItem']", 'unique': 'True', 'primary_key': 'True'}),
            'required_apps': ('merengue.registry.dbfields.RequiredAppsField', [], {}),
            'required_plugins': ('merengue.registry.dbfields.RequiredPluginsField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'registry.registereditem': {
            'Meta': {'object_name': 'RegisteredItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'config': ('merengue.registry.dbfields.ConfigField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['plugin']
