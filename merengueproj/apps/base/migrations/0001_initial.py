# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from base.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'ContactInfo'
        db.create_table('base_contactinfo', (
            ('fax', models.CharField(null=True, max_length=200, verbose_name=_('fax'), blank=True)),
            ('url', models.CharField(null=True, max_length=200, verbose_name=_('url'), blank=True)),
            ('phone', models.CharField(null=True, max_length=200, verbose_name=_('phone'), blank=True)),
            ('contact_email', models.EmailField(null=True, max_length=200, verbose_name=_('contact email'), blank=True)),
            ('contact_email2', models.EmailField(null=True, max_length=200, verbose_name=_('contact email2'), blank=True)),
            ('phone2', models.CharField(null=True, max_length=200, verbose_name=_('phone2'), blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('base', ['ContactInfo'])
        
        # Adding model 'BaseContent'
        db.create_table('base_basecontent', (
            ('name_fr', models.CharField(max_length=200, verbose_name=_('name_fr'), db_index=True)),
            ('contact_info', models.ForeignKey(orm.ContactInfo, editable=False, null=True, verbose_name=_('contact info'), blank=True)),
            ('class_name', models.CharField(editable=False, null=True, max_length=100, verbose_name=_('class name'), db_index=True)),
            ('rank', models.FloatField(default=100.0, editable=False, blank=False, verbose_name=_('rank value'), db_index=True)),
            ('creation_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name=_('creation date'), blank=True)),
            ('description_fr', models.TextField(verbose_name=_('description_fr'), null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('modification_date', models.DateTimeField(auto_now=True, null=True, verbose_name=_('modification date'), blank=True)),
            ('tags', TagField(verbose_name=_('Tags'))),
            ('location', models.ForeignKey(orm['places.Location'], editable=False, null=True, verbose_name=_('location'), blank=True)),
            ('is_autolocated', models.BooleanField(default=False, verbose_name=_("is autolocated"))),
            ('status', models.CharField(_('Publication status'), default='draft', editable=True, max_length=20, db_index=True)),
            ('map_icon', StdImageField(_('map icon'), null=True, upload_to='map_icons', blank=True)),
            ('name_es', models.CharField(max_length=200, verbose_name=_('name_es'), db_index=True)),
            ('description_en', models.TextField(verbose_name=_('description_en'), null=True, blank=True)),
            ('description_es', models.TextField(verbose_name=_('description_es'), null=True, blank=True)),
            ('user_modification_date', models.DateTimeField(editable=False, null=True, verbose_name=_('modification date'), blank=True)),
            ('name_en', models.CharField(max_length=200, verbose_name=_('name_en'), db_index=True)),
            ('last_editor', models.ForeignKey(orm['auth.User'], related_name='last_edited_content', null=True, editable=False, blank=True)),
            ('slug', models.SlugField(max_length=200, verbose_name=_('slug'), db_index=True)),
            ('plain_description_fr', models.TextField(verbose_name=_('plain_description_fr'), null=True, blank=True, editable=False)),
            ('main_image', StdImageField(_('main image'), editable=True, null=True, upload_to='content_images', thumbnail_size=(200,200), blank=True)),
            ('plain_description_es', models.TextField(verbose_name=_('plain_description_es'), null=True, blank=True, editable=False)),
            ('plain_description_en', models.TextField(verbose_name=_('plain_description_en'), null=True, blank=True, editable=False)),
        ))
        db.send_create_signal('base', ['BaseContent'])
        
        # Adding model 'MultimediaRelation'
        db.create_table('base_multimediarelation', (
            ('content', models.ForeignKey(orm.BaseContent, verbose_name=_('content'))),
            ('is_featured', models.BooleanField(default=False, verbose_name=_("is featured"))),
            ('multimedia', models.ForeignKey(orm['multimedia.BaseMultimedia'], verbose_name=_("multimedia"))),
            ('id', models.AutoField(primary_key=True)),
            ('order', models.IntegerField(_("Order"), null=True, blank=True)),
        ))
        db.send_create_signal('base', ['MultimediaRelation'])
        
        # Adding ManyToManyField 'BaseContent.owners'
        db.create_table('base_basecontent_owners', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('basecontent', models.ForeignKey(BaseContent, null=False)),
            ('user', models.ForeignKey(User, null=False))
        ))
        
        # Adding ManyToManyField 'BaseContent.related_items'
        db.create_table('base_basecontent_related_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_basecontent', models.ForeignKey(BaseContent, null=False)),
            ('to_basecontent', models.ForeignKey(BaseContent, null=False))
        ))
        
        # Creating unique_together for [content, multimedia] on MultimediaRelation.
        db.create_unique('base_multimediarelation', ['content_id', 'multimedia_id'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'ContactInfo'
        db.delete_table('base_contactinfo')
        
        # Deleting model 'BaseContent'
        db.delete_table('base_basecontent')
        
        # Deleting model 'MultimediaRelation'
        db.delete_table('base_multimediarelation')
        
        # Dropping ManyToManyField 'BaseContent.owners'
        db.delete_table('base_basecontent_owners')
        
        # Dropping ManyToManyField 'BaseContent.related_items'
        db.delete_table('base_basecontent_related_items')
        
        # Deleting unique_together for [content, multimedia] on MultimediaRelation.
        db.delete_unique('base_multimediarelation', ['content_id', 'multimedia_id'])
        
    
    
    models = {
        'base.basecontent': {
            'Meta': {'ordering': "('name_es',)", 'abstract': 'False', 'permissions': '(("can_draft","Can set as draft"),("can_pending","Can set as pending"),("can_published","Can set as published"),("can_change_is_autolocated","Can edit is_autolocated field"),("can_change_main_image","Can edit main image field"),("can_change_map_icon","Can edit map icon field"),)'},
            'class_name': ('models.CharField', [], {'editable': 'False', 'null': 'True', 'max_length': '100', 'verbose_name': "_('class name')", 'db_index': 'True'}),
            'contact_info': ('models.ForeignKey', ['ContactInfo'], {'editable': 'False', 'null': 'True', 'verbose_name': "_('contact info')", 'blank': 'True'}),
            'creation_date': ('models.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'verbose_name': "_('creation date')", 'blank': 'True'}),
            'description_en': ('models.TextField', [], {'verbose_name': "_('description_en')", 'null': 'True', 'blank': 'True'}),
            'description_es': ('models.TextField', [], {'verbose_name': "_('description_es')", 'null': 'True', 'blank': 'True'}),
            'description_fr': ('models.TextField', [], {'verbose_name': "_('description_fr')", 'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_autolocated': ('models.BooleanField', [], {'default': 'False', 'verbose_name': '_("is autolocated")'}),
            'last_editor': ('models.ForeignKey', ['User'], {'related_name': "'last_edited_content'", 'null': 'True', 'editable': 'False', 'blank': 'True'}),
            'location': ('models.ForeignKey', ['Location'], {'editable': 'False', 'null': 'True', 'verbose_name': "_('location')", 'blank': 'True'}),
            'main_image': ('StdImageField', ["_('main image')"], {'editable': 'True', 'null': 'True', 'upload_to': "'content_images'", 'thumbnail_size': '(200,200)', 'blank': 'True'}),
            'map_icon': ('StdImageField', ["_('map icon')"], {'null': 'True', 'upload_to': "'map_icons'", 'blank': 'True'}),
            'modification_date': ('models.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'verbose_name': "_('modification date')", 'blank': 'True'}),
            'multimedia': ('models.ManyToManyField', ['BaseMultimedia'], {'through': "'MultimediaRelation'", 'verbose_name': "_('multimedia')", 'blank': 'True'}),
            'name_en': ('models.CharField', [], {'max_length' :'200', 'verbose_name': "_('name_en')", 'db_index': 'True'}),
            'name_es': ('models.CharField', [], {'max_length' :'200', 'verbose_name': "_('name_es')", 'db_index': 'True'}),
            'name_fr': ('models.CharField', [], {'max_length' :'200', 'verbose_name': "_('name_fr')", 'db_index': 'True'}),
            'owners': ('models.ManyToManyField', ['User'], {'related_name': "'contents_owned'", 'null': 'True', 'verbose_name': "_('owners')", 'blank': 'True'}),
            'plain_description_en': ('models.TextField', [], {'verbose_name': "_('plain_description_en')", 'null': 'True', 'blank': 'True', 'editable': 'False'}),
            'plain_description_es': ('models.TextField', [], {'verbose_name': "_('plain_description_es')", 'null': 'True', 'blank': 'True', 'editable': 'False'}),
            'plain_description_fr': ('models.TextField', [], {'verbose_name': "_('plain_description_fr')", 'null': 'True', 'blank': 'True', 'editable': 'False'}),
            'rank': ('models.FloatField', [], {'default': '100.0', 'editable': 'False', 'blank': 'False', 'verbose_name': "_('rank value')", 'db_index': 'True'}),
            'related_items': ('models.ManyToManyField', ["'BaseContent'"], {'editable': 'False', 'null': 'True', 'verbose_name': "_('related items')", 'blank': 'True'}),
            'slug': ('models.SlugField', [], {'max_length': '200', 'verbose_name': "_('slug')", 'db_index': 'True'}),
            'status': ('models.CharField', ["_('Publication status')"], {'default': "'draft'", 'editable': 'True', 'max_length': '20', 'db_index': 'True'}),
            'tags': ('TagField', [], {'verbose_name': "_('Tags')"}),
            'user_modification_date': ('models.DateTimeField', [], {'editable': 'False', 'null': 'True', 'verbose_name': "_('modification date')", 'blank': 'True'})
        },
        'multimedia.basemultimedia': {
            'Meta': {'abstract': 'False'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'places.location': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'base.multimediarelation': {
            'Meta': {'ordering': "('order',)", 'unique_together': "('content','multimedia')"},
            'content': ('models.ForeignKey', ['BaseContent'], {'verbose_name': "_('content')"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_featured': ('models.BooleanField', [], {'default': 'False', 'verbose_name': '_("is featured")'}),
            'multimedia': ('models.ForeignKey', ['BaseMultimedia'], {'verbose_name': '_("multimedia")'}),
            'order': ('models.IntegerField', ['_("Order")'], {'null': 'True', 'blank': 'True'})
        },
        'base.contactinfo': {
            'contact_email': ('models.EmailField', [], {'null': 'True', 'max_length': '200', 'verbose_name': "_('contact email')", 'blank': 'True'}),
            'contact_email2': ('models.EmailField', [], {'null': 'True', 'max_length': '200', 'verbose_name': "_('contact email2')", 'blank': 'True'}),
            'fax': ('models.CharField', [], {'null': 'True', 'max_length': '200', 'verbose_name': "_('fax')", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'phone': ('models.CharField', [], {'null': 'True', 'max_length': '200', 'verbose_name': "_('phone')", 'blank': 'True'}),
            'phone2': ('models.CharField', [], {'null': 'True', 'max_length': '200', 'verbose_name': "_('phone2')", 'blank': 'True'}),
            'url': ('models.CharField', [], {'null': 'True', 'max_length': '200', 'verbose_name': "_('url')", 'blank': 'True'})
        }
    }
    
    complete_apps = ['base']
