# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Changing field 'StandingOut.obj_id'
        db.alter_column('standingout_standingout', 'obj_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'StandingOut.obj_content_type'
        db.alter_column('standingout_standingout', 'obj_content_type_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['contenttypes.ContentType']))

    def backwards(self, orm):
        # Changing field 'StandingOut.obj_id'
        db.alter_column('standingout_standingout', 'obj_id', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'StandingOut.obj_content_type'
        db.alter_column('standingout_standingout', 'obj_content_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType']))

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
        },
        'standingout.standingout': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('obj_content_type', 'obj_id', 'related_content_type', 'related_id', 'standing_out_category'),)", 'object_name': 'StandingOut'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'obj_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'standingout_objects'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'obj_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'related_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'standingout_relateds'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'related_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'standing_out_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['standingout.StandingOutCategory']", 'null': 'True', 'blank': 'True'}),
        },
        'standingout.standingoutcategory': {
            'Meta': {'object_name': 'StandingOutCategory'},
            'context_variable': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
        }
    }

    complete_apps = ['standingout']
