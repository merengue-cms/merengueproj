from south.db import db
from django.db import models
from plugins.event.models import *


class Migration:

    def forwards(self, orm):

        # Adding model 'Category'
        db.create_table('event_category', (
            ('id', orm['event.Category:id']),
            ('name_fr', orm['event.Category:name_fr']),
            ('name_es', orm['event.Category:name_es']),
            ('name_en', orm['event.Category:name_en']),
            ('slug', orm['event.Category:slug']),
        ))
        db.send_create_signal('event', ['Category'])

        # Adding model 'Event'
        db.create_table('event_event', (
            ('basecontent_ptr', orm['event.Event:basecontent_ptr']),
            ('publish_date', orm['event.Event:publish_date']),
            ('expire_date', orm['event.Event:expire_date']),
            ('cached_min_start', orm['event.Event:cached_min_start']),
            ('cached_max_end', orm['event.Event:cached_max_end']),
            ('parent', orm['event.Event:parent']),
            ('is_global', orm['event.Event:is_global']),
            ('is_highlight', orm['event.Event:is_highlight']),
            ('frequency', orm['event.Event:frequency']),
        ))
        db.send_create_signal('event', ['Event'])

        # Adding model 'CategoryGroup'
        db.create_table('event_categorygroup', (
            ('id', orm['event.CategoryGroup:id']),
            ('name_fr', orm['event.CategoryGroup:name_fr']),
            ('name_es', orm['event.CategoryGroup:name_es']),
            ('name_en', orm['event.CategoryGroup:name_en']),
            ('slug', orm['event.CategoryGroup:slug']),
            ('hidden_in_global_search', orm['event.CategoryGroup:hidden_in_global_search']),
        ))
        db.send_create_signal('event', ['CategoryGroup'])

        # Adding model 'Occurrence'
        db.create_table('event_occurrence', (
            ('id', orm['event.Occurrence:id']),
            ('location', orm['event.Occurrence:location']),
            ('place', orm['event.Occurrence:place']),
            ('basecontent_location', orm['event.Occurrence:basecontent_location']),
            ('contact_info', orm['event.Occurrence:contact_info']),
            ('event', orm['event.Occurrence:event']),
            ('price_es', orm['event.Occurrence:price_es']),
            ('price_en', orm['event.Occurrence:price_en']),
            ('price_fr', orm['event.Occurrence:price_fr']),
            ('schedule_es', orm['event.Occurrence:schedule_es']),
            ('schedule_en', orm['event.Occurrence:schedule_en']),
            ('schedule_fr', orm['event.Occurrence:schedule_fr']),
            ('start', orm['event.Occurrence:start']),
            ('end', orm['event.Occurrence:end']),
        ))
        db.send_create_signal('event', ['Occurrence'])

        # Adding ManyToManyField 'Category.groups'
        db.create_table('event_category_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm.Category, null=False)),
            ('categorygroup', models.ForeignKey(orm.CategoryGroup, null=False)),
        ))

        # Adding ManyToManyField 'CategoryGroup.sections'
        db.create_table('event_categorygroup_sections', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('categorygroup', models.ForeignKey(orm.CategoryGroup, null=False)),
            ('basesection', models.ForeignKey(orm['section.BaseSection'], null=False))
        ))
        
        # Adding ManyToManyField 'Event.categories'
        db.create_table('event_event_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm.Event, null=False)),
            ('category', models.ForeignKey(orm.Category, null=False))
        ))
        
        # Adding ManyToManyField 'Category.sections'
        db.create_table('event_category_sections', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm.Category, null=False)),
            ('basesection', models.ForeignKey(orm['section.BaseSection'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('event_category')
        
        # Deleting model 'Event'
        db.delete_table('event_event')
        
        # Deleting model 'CategoryGroup'
        db.delete_table('event_categorygroup')
        
        # Deleting model 'Occurrence'
        db.delete_table('event_occurrence')
        
        # Dropping ManyToManyField 'Category.groups'
        db.delete_table('event_category_groups')
        
        # Dropping ManyToManyField 'CategoryGroup.sections'
        db.delete_table('event_categorygroup_sections')
        
        # Dropping ManyToManyField 'Event.categories'
        db.delete_table('event_event_categories')
        
        # Dropping ManyToManyField 'Category.sections'
        db.delete_table('event_category_sections')
        
    
    
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
        'event.category': {
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['event.CategoryGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['section.BaseSection']", 'null': 'True', 'blank': 'True'}),
            'slug': ('cmsutils.db.fields.AutoSlugField', [], {'editable': 'False', 'autofromfield': "'name_es'", 'max_length': '200', 'db_index': 'True'})
        },
        'event.categorygroup': {
            'hidden_in_global_search': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['section.BaseSection']", 'null': 'True', 'blank': 'True'}),
            'slug': ('cmsutils.db.fields.AutoSlugField', [], {'editable': 'False', 'autofromfield': "'name_es'", 'max_length': '200', 'db_index': 'True'})
        },
        'event.event': {
            'basecontent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['base.BaseContent']", 'unique': 'True', 'primary_key': 'True'}),
            'cached_max_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'cached_min_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'to': "orm['event.Category']", 'null': 'True', 'blank': 'True'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'is_global': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'is_highlight': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['event.Event']", 'null': 'True', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'event.occurrence': {
            'basecontent_location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']", 'null': 'True', 'blank': 'True'}),
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.ContactInfo']", 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'occurrence_event'", 'to': "orm['event.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Location']", 'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'price_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'price_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'price_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'schedule_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'schedule_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'schedule_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
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
        'section.basesection': {
            'customstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.CustomStyle']", 'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest_menu': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'interest_menu_section'", 'unique': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'interest_menu_template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'main_document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.Document']", 'null': 'True', 'blank': 'True'}),
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
            'body_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'body_es': ('django.db.models.fields.TextField', [], {}),
            'body_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'carousel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.Carousel']", 'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'floatimage': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_image': ('stdimage.fields.StdImageField', ["_('main image')"], {'editable': 'True', 'null': 'True', 'thumbnail_size': '(200,200)', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'permanent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'photo': ('stdimage.fields.StdImageField', [], {'null': 'True', 'thumbnail_size': '(200,200)', 'blank': 'True'}),
            'photo_description_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'photo_description_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'photo_description_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'plain_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'related_section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.BaseSection']", 'null': 'True', 'blank': 'True'}),
            'search_form': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'search_form_filters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'}),
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
        }
    }
    
    complete_apps = ['event']
