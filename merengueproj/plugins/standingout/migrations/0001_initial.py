# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'StandingOut'
        db.create_table('standingout_standingout', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('obj_content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='standingout_objects', to=orm['contenttypes.ContentType'])),
            ('obj_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('related_content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='standingout_relateds', blank=True, null=True, to=orm['contenttypes.ContentType'])),
            ('related_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('standingout', ['StandingOut'])

    def backwards(self, orm):

        # Deleting model 'StandingOut'
        db.delete_table('standingout_standingout')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
        },
        'standingout.standingout': {
            'Meta': {'object_name': 'StandingOut'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'obj_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'standingout_objects'", 'to': "orm['contenttypes.ContentType']"}),
            'obj_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'related_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'standingout_relateds'", 'blank': 'True', 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'related_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
        }
    }

    complete_apps = ['standingout']
