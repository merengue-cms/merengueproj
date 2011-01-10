# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Collection'
        db.create_table('collection_collection', (
            ('basecontent_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['base.BaseContent'], unique=True, primary_key=True)),
            ('group_by', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('order_by', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('reverse_order', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('collection', ['Collection'])

        # Adding M2M table for field content_types on 'Collection'
        db.create_table('collection_collection_content_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('collection', models.ForeignKey(orm['collection.collection'], null=False)),
            ('contenttype', models.ForeignKey(orm['contenttypes.contenttype'], null=False)),
        ))
        db.create_unique('collection_collection_content_types', ['collection_id', 'contenttype_id'])

        # Adding model 'IncludeCollectionFilter'
        db.create_table('collection_includecollectionfilter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filter_field', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('filter_operator', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('filter_value', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(related_name='include_filters', to=orm['collection.Collection'])),
        ))
        db.send_create_signal('collection', ['IncludeCollectionFilter'])

        # Adding model 'ExcludeCollectionFilter'
        db.create_table('collection_excludecollectionfilter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filter_field', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('filter_operator', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('filter_value', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(related_name='exclude_filters', to=orm['collection.Collection'])),
        ))
        db.send_create_signal('collection', ['ExcludeCollectionFilter'])

        # Adding model 'CollectionDisplayField'
        db.create_table('collection_collectiondisplayfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('field_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(related_name='display_fields', to=orm['collection.Collection'])),
            ('safe', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('collection', ['CollectionDisplayField'])

    def backwards(self, orm):

        # Deleting model 'Collection'
        db.delete_table('collection_collection')

        # Removing M2M table for field content_types on 'Collection'
        db.delete_table('collection_collection_content_types')

        # Deleting model 'IncludeCollectionFilter'
        db.delete_table('collection_includecollectionfilter')

        # Deleting model 'ExcludeCollectionFilter'
        db.delete_table('collection_excludecollectionfilter')

        # Deleting model 'CollectionDisplayField'
        db.delete_table('collection_collectiondisplayfield')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
        },
        'base.basecontent': {
            'Meta': {'object_name': 'BaseContent'},
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'commentable': ('django.db.models.fields.CharField', [], {'default': "'allowed'", 'max_length': '20'}),
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.ContactInfo']", 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            
            
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_editor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_edited_content'", 'null': 'True', 'to': "orm['auth.User']"}),
            'main_image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'map_icon': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'meta_desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'multimedia': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.BaseMultimedia']", 'symmetrical': 'False', 'through': "'MultimediaRelation'", 'blank': 'True'}),
            
            
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contents_owned'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            
            
            'rank': ('django.db.models.fields.FloatField', [], {'default': '100.0', 'db_index': 'True'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.BaseContent']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
            'user_modification_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
        },
        'base.contactinfo': {
            'Meta': {'object_name': 'ContactInfo'},
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'contact_email2': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
        },
        'base.multimediarelation': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('content', 'multimedia'),)", 'object_name': 'MultimediaRelation'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multimedia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multimedia.BaseMultimedia']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
        },
        'collection.collection': {
            'Meta': {'object_name': 'Collection', '_ormbases': ['base.BaseContent']},
            'basecontent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['base.BaseContent']", 'unique': 'True', 'primary_key': 'True'}),
            'content_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['contenttypes.ContentType']", 'symmetrical': 'False'}),
            'group_by': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'order_by': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'reverse_order': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
        },
        'collection.collectiondisplayfield': {
            'Meta': {'object_name': 'CollectionDisplayField'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'display_fields'", 'to': "orm['collection.Collection']"}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'field_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'safe': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
        },
        'collection.excludecollectionfilter': {
            'Meta': {'object_name': 'ExcludeCollectionFilter'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'exclude_filters'", 'to': "orm['collection.Collection']"}),
            'filter_field': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'filter_operator': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'filter_value': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
        },
        'collection.includecollectionfilter': {
            'Meta': {'object_name': 'IncludeCollectionFilter'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'include_filters'", 'to': "orm['collection.Collection']"}),
            'filter_field': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'filter_operator': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'filter_value': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
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
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
        },
    }

    complete_apps = ['collection']
