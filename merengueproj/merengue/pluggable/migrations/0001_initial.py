# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

from merengue.base.utils import table_exists


class Migration(SchemaMigration):

    def forwards(self, orm):
        if table_exists('plugins_registeredplugin'):
            return  # already migrated
        # Adding model 'RegisteredPlugin'
        db.create_table('plugins_registeredplugin', (
            ('registereditem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['registry.RegisteredItem'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('required_apps', self.gf('merengue.pluggable.dbfields.RequiredAppsField')()),
            ('required_plugins', self.gf('merengue.pluggable.dbfields.RequiredPluginsField')()),
            ('installed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('directory_name', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True)),
        ))
        db.send_create_signal('pluggable', ['RegisteredPlugin'])

    def backwards(self, orm):
        # Deleting model 'RegisteredPlugin'
        db.delete_table('plugins_registeredplugin')

    models = {
        'pluggable.registeredplugin': {
            'Meta': {'object_name': 'RegisteredPlugin', 'db_table': "'plugins_registeredplugin'", '_ormbases': ['registry.RegisteredItem']},
            'directory_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'installed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
