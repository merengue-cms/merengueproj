# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.


from south.db import db
from django.db import models
from django.conf import settings
from merengue.section.models import *


class Migration:

    def forwards(self, orm):
        "Write your forwards migration here"
        if db.backend_name == 'mysql':
            db.execute('ALTER TABLE `section_basesection_related_content` ADD COLUMN `order` integer UNSIGNED NOT NULL')
            db.execute('UPDATE `section_basesection_related_content` SET `order` = 0')
        else:
            db.execute('ALTER TABLE "section_basesection_related_content" ADD COLUMN "order" integer CHECK ("order" >= 0)')
            db.execute('UPDATE "section_basesection_related_content" SET "order" = 0')

    def backwards(self, orm):
        "Write your backwards migration here"

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
            
            
            
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_autolocated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_editor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_edited_content'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Location']", 'null': 'True', 'blank': 'True'}),
            'main_image': ('stdimage.fields.StdImageField', ["_('main image')"], {'editable': 'True', 'null': 'True', 'thumbnail_size': '(200,200)', 'blank': 'True'}),
            'map_icon': ('stdimage.fields.StdImageField', ["_('map icon')"], {'null': 'True', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'multimedia': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.BaseMultimedia']", 'blank': 'True'}),
            
            
            
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            
            
            
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
            
            
            
            'image': ('stdimage.fields.StdImageField', [], {'max_length': '200', 'thumbnail_size': '(200,200)'}),
            'plone_uid': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'places.location': {
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
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
            
            
            
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest_menu': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'interest_menu_section'", 'unique': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'interest_menu_template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'main_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_main_content'", 'blank': 'True', 'null': 'True', 'to': "orm['base.BaseContent']"}),
            'main_image': ('stdimage.fields.StdImageField', ["_('main image')"], {'editable': 'True', 'null': 'True', 'thumbnail_size': '(200,200)', 'blank': 'True'}),
            'main_menu': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'main_menu_section'", 'unique': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'main_menu_template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            
            
            
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            
            
            
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
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"})
        },
        'section.customstyle': {
            'color_1': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True'}),
            'color_2': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True'}),
            'color_3': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True'}),
            'content_head_background': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu_head_background': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'menu_link_color': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True'}),
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
            
            
            
            'search_form': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'search_form_filters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'section.documentsection': {
            
            
            
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': "orm['section.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {})
        },
        'section.menu': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            
            
            
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child_set'", 'blank': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'section.section': {
            'basesection_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseSection']", 'unique': 'True', 'primary_key': 'True'})
        },
        'section.sectionrelatedcontent': {
            'Meta': {'db_table': "'section_basesection_related_content'"},
            'basecontent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'basesection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.BaseSection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    if not settings.USE_GIS:
        del models['places.location']
        del models['base.basecontent']['location']
        del models['base.basecontent']['map_icon']
        del models['base.basecontent']['is_autolocated']

    complete_apps = ['section']
