# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RegisteredBlock.fixed_place'
        db.add_column('block_registeredblock', 'fixed_place', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

    def backwards(self, orm):
        # Deleting field 'RegisteredBlock.fixed_place'
        db.delete_column('block_registeredblock', 'fixed_place')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'base.basecontent': {
            'Meta': {'ordering': "('position', 'name_en')", 'object_name': 'BaseContent'},
            'adquire_global_permissions': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cached_plain_text_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cached_plain_text_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cached_plain_text_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'commentable': ('django.db.models.fields.CharField', [], {'default': "'allowed'", 'max_length': '20'}),
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.ContactInfo']", 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'has_related_blocks': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_editor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_edited_content'", 'null': 'True', 'to': "orm['auth.User']"}),
            'main_image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'meta_desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'multimedia': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.BaseMultimedia']", 'symmetrical': 'False', 'through': "orm['base.MultimediaRelation']", 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'no_changeable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_changeable_fields': ('merengue.base.dbfields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'no_deletable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contents_owned'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'plain_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'rank': ('django.db.models.fields.FloatField', [], {'default': '100.0', 'db_index': 'True'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.BaseContent']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'user_modification_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'base.contactinfo': {
            'Meta': {'object_name': 'ContactInfo'},
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'contact_email2': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'base.multimediarelation': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('content', 'multimedia'),)", 'object_name': 'MultimediaRelation'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multimedia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multimedia.BaseMultimedia']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'block.registeredblock': {
            'Meta': {'ordering': "('order',)", 'object_name': 'RegisteredBlock', '_ormbases': ['registry.RegisteredItem']},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']", 'null': 'True'}),
            'fixed_place': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hidden_in_urls': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'is_fixed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'overwrite_always': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'overwrite_if_place': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'placed_at': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registereditem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['registry.RegisteredItem']", 'unique': 'True', 'primary_key': 'True'}),
            'shown_in_urls': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'multimedia.basemultimedia': {
            'Meta': {'object_name': 'BaseMultimedia'},
            'authors': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_editor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'registry.registereditem': {
            'Meta': {'ordering': "('order',)", 'object_name': 'RegisteredItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'broken': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'config': ('merengue.registry.dbfields.ConfigField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'traceback': ('django.db.models.fields.TextField', [], {'default': "''"})
        }
    }

    complete_apps = ['block']
