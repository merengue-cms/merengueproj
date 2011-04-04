# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from merengue.base.utils import (delete_south_trans_column,
                                 add_south_trans_column, add_south_trans_fields)


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'StandingOut.short_description'
        add_south_trans_column(
            table='standingout_standingout',
            model_name='standingout.standingout',
            field_name='short_description',
            orm=orm,
        )


    def backwards(self, orm):
        
        # Deleting field 'StandingOut.short_description'
        delete_south_trans_column(
            table='standingout_standingout',
            field_name='short_description',
        )


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'standingout.standingout': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('obj_content_type', 'obj_id', 'related_content_type', 'related_id', 'standing_out_category'),)", 'object_name': 'StandingOut'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'obj_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'standingout_objects'", 'to': "orm['contenttypes.ContentType']"}),
            'obj_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'related_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'standingout_relateds'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'related_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'standing_out_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['standingout.StandingOutCategory']", 'null': 'True', 'blank': 'True'}),
        },
        'standingout.standingoutcategory': {
            'Meta': {'object_name': 'StandingOutCategory'},
            'context_variable': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'})
        }
    }
    add_south_trans_fields(models, {
        'standingout.standingout': {
            'short_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
        },
    })

    complete_apps = ['standingout']
