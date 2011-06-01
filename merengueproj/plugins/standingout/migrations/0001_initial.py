# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

from merengue.base.utils import table_exists
from merengue.base.utils import south_trans_data, add_south_trans_fields


class Migration(SchemaMigration):

    def forwards(self, orm):

        if table_exists('standingout_standingoutcategory'):
            return

        data = (
            ('id', orm['standingout.standingoutcategory:id']),
            ('slug', orm['standingout.standingoutcategory:slug']),
            ('context_variable', orm['standingout.standingoutcategory:context_variable']),
        )

        data = data + south_trans_data(
            orm=orm,
            trans_data={
                'standingout.standingoutcategory': ('name', ),
            },
        )

        # Adding model 'StandingOutCategory'
        db.create_table('standingout_standingoutcategory', data)
        db.send_create_signal('standingout', ['StandingOutCategory'])

        # Adding model 'StandingOut'
        db.create_table('standingout_standingout', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('obj_content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='standingout_objects', to=orm['contenttypes.ContentType'])),
            ('obj_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('related_content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='standingout_relateds', null=True, to=orm['contenttypes.ContentType'])),
            ('related_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True, null=True, blank=True)),
            ('standing_out_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['standingout.StandingOutCategory'], null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('standingout', ['StandingOut'])

        # Adding unique constraint on 'StandingOut', fields ['obj_content_type', 'obj_id', 'related_content_type', 'related_id', 'standing_out_category']
        db.create_unique('standingout_standingout', ['obj_content_type_id', 'obj_id', 'related_content_type_id', 'related_id', 'standing_out_category_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'StandingOut', fields ['obj_content_type', 'obj_id', 'related_content_type', 'related_id', 'standing_out_category']
        db.delete_unique('standingout_standingout', ['obj_content_type_id', 'obj_id', 'related_content_type_id', 'related_id', 'standing_out_category_id'])

        # Deleting model 'StandingOutCategory'
        db.delete_table('standingout_standingoutcategory')

        # Deleting model 'StandingOut'
        db.delete_table('standingout_standingout')

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
            'standing_out_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['standingout.StandingOutCategory']", 'null': 'True', 'blank': 'True'})
        },
        'standingout.standingoutcategory': {
            'Meta': {'object_name': 'StandingOutCategory'},
            'context_variable': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'})
        }
    }
    add_south_trans_fields(models, {
        'standingout.standingoutcategory': {
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
        },
    })

    complete_apps = ['standingout']
