# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

from merengue.base.utils import table_exists


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RegisteredBlock'
        if table_exists('block_registeredblock'):
            return  # already migrated
        db.create_table('block_registeredblock', (
            ('registereditem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['registry.RegisteredItem'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('placed_at', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('block', ['RegisteredBlock'])

    def backwards(self, orm):
        # Deleting model 'RegisteredBlock'
        db.delete_table('block_registeredblock')

    models = {
        'block.registeredblock': {
            'Meta': {'object_name': 'RegisteredBlock', '_ormbases': ['registry.RegisteredItem']},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'placed_at': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registereditem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['registry.RegisteredItem']", 'unique': 'True', 'primary_key': 'True'}),
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

    complete_apps = ['block']
