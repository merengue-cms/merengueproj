# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RegisteredPlugin.meta_info'
        db.add_column('plugins_registeredplugin', 'meta_info', self.gf('merengue.base.dbfields.JSONField')(null=True), keep_default=False)

    def backwards(self, orm):
        # Deleting field 'RegisteredPlugin.meta_info'
        db.delete_column('plugins_registeredplugin', 'meta_info')

    models = {
        'pluggable.registeredplugin': {
            'Meta': {'object_name': 'RegisteredPlugin', 'db_table': "'plugins_registeredplugin'", '_ormbases': ['registry.RegisteredItem']},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'directory_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'installed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'meta_info': ('merengue.base.dbfields.JSONField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registereditem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['registry.RegisteredItem']", 'unique': 'True', 'primary_key': 'True'}),
            'required_apps': ('merengue.pluggable.dbfields.RequiredAppsField', [], {}),
            'required_plugins': ('merengue.pluggable.dbfields.RequiredPluginsField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
        },
        'registry.registereditem': {
            'Meta': {'object_name': 'RegisteredItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'broken': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'config': ('merengue.registry.dbfields.ConfigField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'traceback': ('django.db.models.fields.TextField', [], {'default': "''"}),
        }
    }

    complete_apps = ['pluggable']
