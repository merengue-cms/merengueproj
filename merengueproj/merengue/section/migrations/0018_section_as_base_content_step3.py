# encoding: utf-8
from django.conf import settings
from django.db import models
from south.db import db
from south.v2 import SchemaMigration
from transmeta import get_real_fieldname

from merengue.base.utils import add_south_trans_fields


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'BaseSection.status'
        db.delete_column('section_basesection', 'status')

        # Deleting field 'BaseSection.slug'
        db.delete_column('section_basesection', 'slug')

        # Deleting field 'BaseSection.main_image'
        db.delete_column('section_basesection', 'main_image')

        # Deleting field 'BaseSection.id'
        db.delete_column('section_basesection', 'id')

        for field in ('name', 'description', 'plain_description', ):
            for lang, lang_name in settings.LANGUAGES:
                db.delete_column('section_basesection', get_real_fieldname(field, lang))

        # Swapping primary key from id to basecontent_ptr_id
        db.create_primary_key('section_basesection', ['basecontent_ptr_id'])

        # Add new foreign key to section_basesection_related_content.basesection_id
        db.alter_column('section_basesection_related_content', 'basesection_id', models.ForeignKey(orm['section.BaseSection'], null=False, blank=False))

    def backwards(self, orm):
        # Adding model 'Section'
        db.create_table('section_section', (
            ('basesection_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['section.BaseSection'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('section', ['Section'])

        # Adding field 'BaseSection.status'
        db.add_column('section_basesection', 'status', self.gf('django.db.models.fields.CharField')(default='draft', max_length=20, db_index=True), keep_default=False)

        # Adding field 'BaseSection.slug'
        db.add_column('section_basesection', 'slug', self.gf('django.db.models.fields.SlugField')(default='', unique=True, max_length=200, db_index=True), keep_default=False)

        # Adding field 'BaseSection.main_image'
        db.add_column('section_basesection', 'main_image', self.gf('stdimage.fields.StdImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'BaseSection.id'
        db.add_column('section_basesection', 'id', self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True), keep_default=False)

        # Swapping primary key from basecontent_ptr_id to id
        db.delete_primary_key('section_basesection')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
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
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'}),
        },
        'base.basecontent': {
            'Meta': {'object_name': 'BaseContent'},
            'adquire_global_permissions': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'commentable': ('django.db.models.fields.CharField', [], {'default': "'allowed'", 'max_length': '20'}),
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.ContactInfo']", 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'has_related_blocks': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_editor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_edited_content'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'main_image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'meta_desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'multimedia': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.BaseMultimedia']", 'symmetrical': 'False', 'through': "'MultimediaRelation'", 'blank': 'True'}),
            'no_changeable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_changeable_fields': ('merengue.base.dbfields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'no_deletable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'contents_owned'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'rank': ('django.db.models.fields.FloatField', [], {'default': '100.0', 'db_index': 'True'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['base.BaseContent']", 'symmetrical': 'False', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'unique': 'True', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'user_modification_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'tags': ('tagging.fields.TagField', [], {}),
        },
        'registry.registereditem': {
            'Meta': {'ordering': "('order',)", 'object_name': 'RegisteredItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'broken': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'config': ('merengue.registry.dbfields.ConfigField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'traceback': ('django.db.models.fields.TextField', [], {'default': "''"}),
        },
        'section.absolutelink': {
            'Meta': {'object_name': 'AbsoluteLink', '_ormbases': ['section.BaseLink']},
            'baselink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseLink']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
        },
        'section.baselink': {
            'Meta': {'object_name': 'BaseLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.Menu']", 'unique': 'True'}),
        },
        'section.basesection': {
            'Meta': {'ordering': "('order',)", 'object_name': 'BaseSection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'basecontent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['base.BaseContent']", 'unique': 'True', 'primary_key': 'True'}),
            'customstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.CustomStyle']", 'null': 'True', 'blank': 'True'}),
            'main_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_main_content'", 'blank': 'True', 'null': 'True', 'to': "orm['base.BaseContent']"}),
            'main_menu': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'main_menu_section'", 'unique': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'related_content': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sections'", 'symmetrical': 'False', 'through': "'SectionRelatedContent'", 'to': "orm['base.BaseContent']"}),
        },
        'section.contentlink': {
            'Meta': {'object_name': 'ContentLink', '_ormbases': ['section.BaseLink']},
            'baselink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseLink']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
        },
        'section.customstyle': {
            'Meta': {'object_name': 'CustomStyle'},
            'css_chunk': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
        },
        'section.customstyleimage': {
            'Meta': {'object_name': 'CustomStyleImage'},
            'custom_css_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'customstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.CustomStyle']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
        },
        'section.document': {
            'Meta': {'object_name': 'Document', '_ormbases': ['base.BaseContent']},
            'basecontent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['base.BaseContent']", 'unique': 'True', 'primary_key': 'True'}),
            'permanent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
        },
        'section.documentsection': {
            'Meta': {'ordering': "('position',)", 'object_name': 'DocumentSection'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'document_sections'", 'to': "orm['section.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
        },
        'section.menu': {
            'Meta': {'object_name': 'Menu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child_set'", 'blank': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
        },
        'section.sectionrelatedcontent': {
            'Meta': {'object_name': 'SectionRelatedContent', 'db_table': "'section_basesection_related_content'"},
            'basecontent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'basesection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sectionrelatedcontent'", 'to': "orm['section.BaseSection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
        },
        'section.viewletlink': {
            'Meta': {'object_name': 'ViewletLink', '_ormbases': ['section.BaseLink']},
            'baselink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseLink']", 'unique': 'True', 'primary_key': 'True'}),
            'viewlet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['viewlet.RegisteredViewlet']"}),
        },
        'viewlet.registeredviewlet': {
            'Meta': {'ordering': "('order',)", 'object_name': 'RegisteredViewlet', '_ormbases': ['registry.RegisteredItem']},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registereditem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['registry.RegisteredItem']", 'unique': 'True', 'primary_key': 'True'}),
        }
    }
    add_south_trans_fields(models, {
        'base.basecontent': {
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cached_plain_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
        },
    })

    complete_apps = ['section']
