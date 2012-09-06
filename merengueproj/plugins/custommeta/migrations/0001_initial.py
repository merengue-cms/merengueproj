# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'CustomMeta'
        db.create_table('custommeta_custommeta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url_regexp', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('custommeta', ['CustomMeta'])

    def backwards(self, orm):

        # Deleting model 'CustomMeta'
        db.delete_table('custommeta_custommeta')

    models = {
        'custommeta.custommeta': {
            'Meta': {'object_name': 'CustomMeta'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'url_regexp': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['custommeta']
