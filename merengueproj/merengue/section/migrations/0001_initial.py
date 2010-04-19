
from south.db import db
from django.db import models
from django.conf import settings
from merengue.section.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'BaseSection'
        db.create_table('section_basesection', (
            ('id', orm['section.BaseSection:id']),
            ('name_fr', orm['section.BaseSection:name_fr']),
            ('name_es', orm['section.BaseSection:name_es']),
            ('name_en', orm['section.BaseSection:name_en']),
            ('slug', orm['section.BaseSection:slug']),
            ('plain_description_fr', orm['section.BaseSection:plain_description_fr']),
            ('plain_description_es', orm['section.BaseSection:plain_description_es']),
            ('plain_description_en', orm['section.BaseSection:plain_description_en']),
            ('description_fr', orm['section.BaseSection:description_fr']),
            ('description_en', orm['section.BaseSection:description_en']),
            ('description_es', orm['section.BaseSection:description_es']),
            ('status', orm['section.BaseSection:status']),
            ('main_image', orm['section.BaseSection:main_image']),
            ('main_menu', orm['section.BaseSection:main_menu']),
            ('secondary_menu', orm['section.BaseSection:secondary_menu']),
            ('interest_menu', orm['section.BaseSection:interest_menu']),
            ('main_menu_template', orm['section.BaseSection:main_menu_template']),
            ('secondary_menu_template', orm['section.BaseSection:secondary_menu_template']),
            ('interest_menu_template', orm['section.BaseSection:interest_menu_template']),
            ('main_content', orm['section.BaseSection:main_content']),
            ('customstyle', orm['section.BaseSection:customstyle']),
        ))
        db.send_create_signal('section', ['BaseSection'])
        
        # Adding model 'ContentLink'
        db.create_table('section_contentlink', (
            ('baselink_ptr', orm['section.ContentLink:baselink_ptr']),
            ('content', orm['section.ContentLink:content']),
        ))
        db.send_create_signal('section', ['ContentLink'])
        
        # Adding model 'Menu'
        db.create_table('section_menu', (
            ('id', orm['section.Menu:id']),
            ('name_es', orm['section.Menu:name_es']),
            ('name_fr', orm['section.Menu:name_fr']),
            ('name_en', orm['section.Menu:name_en']),
            ('slug', orm['section.Menu:slug']),
            ('parent', orm['section.Menu:parent']),
            ('url', orm['section.Menu:url']),
            ('lft', orm['section.Menu:lft']),
            ('rght', orm['section.Menu:rght']),
            ('tree_id', orm['section.Menu:tree_id']),
            ('level', orm['section.Menu:level']),
        ))
        db.send_create_signal('section', ['Menu'])
        
        # Adding model 'AppSection'
        db.create_table('section_appsection', (
            ('basesection_ptr', orm['section.AppSection:basesection_ptr']),
        ))
        db.send_create_signal('section', ['AppSection'])
        
        # Adding model 'Document'
        db.create_table('section_document', (
            ('basecontent_ptr', orm['section.Document:basecontent_ptr']),
            ('photo', orm['section.Document:photo']),
            ('floatimage', orm['section.Document:floatimage']),
            ('photo_description_en', orm['section.Document:photo_description_en']),
            ('photo_description_es', orm['section.Document:photo_description_es']),
            ('photo_description_fr', orm['section.Document:photo_description_fr']),
            ('carousel', orm['section.Document:carousel']),
            ('search_form', orm['section.Document:search_form']),
            ('search_form_filters', orm['section.Document:search_form_filters']),
            ('related_section', orm['section.Document:related_section']),
            ('permanent', orm['section.Document:permanent']),
        ))
        db.send_create_signal('section', ['Document'])
        
        # Adding model 'Carousel'
        db.create_table('section_carousel', (
            ('id', orm['section.Carousel:id']),
            ('name', orm['section.Carousel:name']),
            ('slug', orm['section.Carousel:slug']),
        ))
        db.send_create_signal('section', ['Carousel'])
        
        # Adding model 'AbsoluteLink'
        db.create_table('section_absolutelink', (
            ('baselink_ptr', orm['section.AbsoluteLink:baselink_ptr']),
            ('url', orm['section.AbsoluteLink:url']),
        ))
        db.send_create_signal('section', ['AbsoluteLink'])
        
        # Adding model 'Section'
        db.create_table('section_section', (
            ('basesection_ptr', orm['section.Section:basesection_ptr']),
        ))
        db.send_create_signal('section', ['Section'])
        
        # Adding model 'BaseLink'
        db.create_table('section_baselink', (
            ('id', orm['section.BaseLink:id']),
            ('menu', orm['section.BaseLink:menu']),
        ))
        db.send_create_signal('section', ['BaseLink'])
        
        # Adding model 'CustomStyle'
        db.create_table('section_customstyle', (
            ('id', orm['section.CustomStyle:id']),
            ('color_1', orm['section.CustomStyle:color_1']),
            ('color_2', orm['section.CustomStyle:color_2']),
            ('color_3', orm['section.CustomStyle:color_3']),
            ('menu_link_color', orm['section.CustomStyle:menu_link_color']),
            ('searcher_left_arrow', orm['section.CustomStyle:searcher_left_arrow']),
            ('searcher_right_arrow', orm['section.CustomStyle:searcher_right_arrow']),
            ('searcher_tab_image', orm['section.CustomStyle:searcher_tab_image']),
            ('searcher_last_tab_image', orm['section.CustomStyle:searcher_last_tab_image']),
            ('search_results_item_background', orm['section.CustomStyle:search_results_item_background']),
            ('menu_head_background', orm['section.CustomStyle:menu_head_background']),
            ('content_head_background', orm['section.CustomStyle:content_head_background']),
        ))
        db.send_create_signal('section', ['CustomStyle'])
        
        # Adding ManyToManyField 'Carousel.class_name'
        db.create_table('section_carousel_class_name', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('carousel', models.ForeignKey(orm.Carousel, null=False)),
            ('contenttype', models.ForeignKey(orm['contenttypes.ContentType'], null=False))
        ))
        
        # Adding ManyToManyField 'Carousel.photo_list'
        db.create_table('section_carousel_photo_list', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('carousel', models.ForeignKey(orm.Carousel, null=False)),
            ('photo', models.ForeignKey(orm['multimedia.Photo'], null=False))
        ))
        
        # Adding ManyToManyField 'Document.videos'
        db.create_table('section_document_videos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('document', models.ForeignKey(orm.Document, null=False)),
            ('video', models.ForeignKey(orm['multimedia.Video'], null=False))
        ))
        
        # Adding ManyToManyField 'BaseSection.related_content'
        db.create_table('section_basesection_related_content', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('basesection', models.ForeignKey(orm.BaseSection, null=False)),
            ('basecontent', models.ForeignKey(orm['base.BaseContent'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'BaseSection'
        db.delete_table('section_basesection')
        
        # Deleting model 'ContentLink'
        db.delete_table('section_contentlink')
        
        # Deleting model 'Menu'
        db.delete_table('section_menu')
        
        # Deleting model 'AppSection'
        db.delete_table('section_appsection')
        
        # Deleting model 'Document'
        db.delete_table('section_document')
        
        # Deleting model 'Carousel'
        db.delete_table('section_carousel')
        
        # Deleting model 'AbsoluteLink'
        db.delete_table('section_absolutelink')
        
        # Deleting model 'Section'
        db.delete_table('section_section')
        
        # Deleting model 'BaseLink'
        db.delete_table('section_baselink')
        
        # Deleting model 'CustomStyle'
        db.delete_table('section_customstyle')
        
        # Dropping ManyToManyField 'Carousel.class_name'
        db.delete_table('section_carousel_class_name')
        
        # Dropping ManyToManyField 'Carousel.photo_list'
        db.delete_table('section_carousel_photo_list')
        
        # Dropping ManyToManyField 'Document.videos'
        db.delete_table('section_document_videos')
        
        # Dropping ManyToManyField 'BaseSection.related_content'
        db.delete_table('section_basesection_related_content')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'base.basecontent': {
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.ContactInfo']", 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_autolocated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_editor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_edited_content'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Location']", 'null': 'True', 'blank': 'True'}),
            'main_image': ('stdimage.fields.StdImageField', ["_('main image')"], {'editable': 'True', 'null': 'True', 'thumbnail_size': '(200,200)', 'blank': 'True'}),
            'map_icon': ('stdimage.fields.StdImageField', ["_('map icon')"], {'null': 'True', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'multimedia': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.BaseMultimedia']", 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'plain_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.FloatField', [], {'default': '100.0', 'db_index': 'True'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['base.BaseContent']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'user_modification_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'base.contactinfo': {
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'contact_email2': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'multimedia.basemultimedia': {
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
        'multimedia.photo': {
            'basemultimedia_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['multimedia.BaseMultimedia']", 'unique': 'True', 'primary_key': 'True'}),
            'caption_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'caption_es': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'caption_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'image': ('stdimage.fields.StdImageField', [], {'max_length': '200', 'thumbnail_size': '(200,200)'}),
            'plone_uid': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'multimedia.video': {
            'basemultimedia_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['multimedia.BaseMultimedia']", 'unique': 'True', 'primary_key': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'plone_uid': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'preview': ('stdimage.fields.StdImageField', [], {'null': 'True', 'thumbnail_size': '(200,200)', 'blank': 'True'})
        },
        'places.location': {
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'borders': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'section.absolutelink': {
            'baselink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseLink']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'section.appsection': {
            'basesection_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseSection']", 'unique': 'True', 'primary_key': 'True'})
        },
        'section.baselink': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.Menu']", 'unique': 'True'})
        },
        'section.basesection': {
            'customstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.CustomStyle']", 'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest_menu': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'interest_menu_section'", 'unique': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'interest_menu_template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'main_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_main_content'", 'blank': 'True', 'null': 'True', 'to': "orm['base.BaseContent']"}),
            'main_image': ('stdimage.fields.StdImageField', ["_('main image')"], {'editable': 'True', 'null': 'True', 'thumbnail_size': '(200,200)', 'blank': 'True'}),
            'main_menu': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'main_menu_section'", 'unique': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'main_menu_template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'plain_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'related_content': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['base.BaseContent']"}),
            'secondary_menu': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'secondary_menu_section'", 'unique': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'secondary_menu_template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'})
        },
        'section.carousel': {
            'class_name': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'photo_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.Photo']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'section.contentlink': {
            'baselink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseLink']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['base.BaseContent']", 'unique': 'True'})
        },
        'section.customstyle': {
            'color_1': ('cmsutils.db.fields.ColorField', [], {'null': 'True', 'blank': 'True'}),
            'color_2': ('cmsutils.db.fields.ColorField', [], {'null': 'True', 'blank': 'True'}),
            'color_3': ('cmsutils.db.fields.ColorField', [], {'null': 'True', 'blank': 'True'}),
            'content_head_background': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu_head_background': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'menu_link_color': ('cmsutils.db.fields.ColorField', [], {'null': 'True', 'blank': 'True'}),
            'search_results_item_background': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'searcher_last_tab_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'searcher_left_arrow': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'searcher_right_arrow': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'searcher_tab_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'section.document': {
            'basecontent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['base.BaseContent']", 'unique': 'True', 'primary_key': 'True'}),
            'carousel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.Carousel']", 'null': 'True', 'blank': 'True'}),
            'floatimage': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'permanent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'photo': ('stdimage.fields.StdImageField', [], {'null': 'True', 'thumbnail_size': '(200,200)', 'blank': 'True'}),
            'photo_description_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'photo_description_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'photo_description_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'related_section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.BaseSection']", 'null': 'True', 'blank': 'True'}),
            'search_form': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'search_form_filters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.Video']", 'null': 'True', 'blank': 'True'})
        },
        'section.menu': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child_set'", 'blank': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'section.section': {
            'basesection_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseSection']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    if not settings.USE_GIS:
        del models['places.location']
        del models['base.basecontent']['location']
        del models['base.basecontent']['map_icon']
        del models['base.basecontent']['is_autolocated']
    
    complete_apps = ['section']
