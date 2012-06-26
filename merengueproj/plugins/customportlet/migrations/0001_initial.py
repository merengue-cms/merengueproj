# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CustomPortlet'
        db.create_table('customportlet_customportlet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name_es', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=200, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=200, db_index=True)),
            ('plain_description_es', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('plain_description_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_es', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='draft', max_length=20, db_index=True)),
            ('main_image', self.gf('stdimage.fields.StdImageField')(max_length=100, null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('link_color', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('background', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('customportlet', ['CustomPortlet'])

    def backwards(self, orm):
        # Deleting model 'CustomPortlet'
        db.delete_table('customportlet_customportlet')

    models = {
        'customportlet.customportlet': {
            'Meta': {'ordering': "('order',)", 'object_name': 'CustomPortlet'},
            'background': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'link_color': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'main_image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'plain_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'})
        }
    }

    complete_apps = ['customportlet']
