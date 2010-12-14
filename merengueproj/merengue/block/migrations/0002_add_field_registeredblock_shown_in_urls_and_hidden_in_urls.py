# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RegisteredBlock.shown_in_urls'
        db.add_column('block_registeredblock', 'shown_in_urls', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Adding field 'RegisteredBlock.hidden_in_urls'
        db.add_column('block_registeredblock', 'hidden_in_urls', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

    def backwards(self, orm):
        # Deleting field 'RegisteredBlock.shown_in_urls'
        db.delete_column('block_registeredblock', 'shown_in_urls')

        # Deleting field 'RegisteredBlock.hidden_in_urls'
        db.delete_column('block_registeredblock', 'hidden_in_urls')

    models = {
        'block.registeredblock': {
            'Meta': {'object_name': 'RegisteredBlock', '_ormbases': ['registry.RegisteredItem']},
            'hidden_in_urls': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'placed_at': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registereditem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['registry.RegisteredItem']", 'unique': 'True', 'primary_key': 'True'}),
            'shown_in_urls': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
