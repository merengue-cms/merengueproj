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

# encoding: utf-8
import datetime
from django.conf import settings
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from merengue.base.utils import (south_trans_data, add_south_trans_fields,
                                 add_south_trans_column, delete_south_trans_column)


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'basesection.main_menu_template'
        db.delete_column('section_basesection', 'main_menu_template')

        # Deleting field 'basesection.interest_menu'
        db.delete_column('section_basesection', 'interest_menu_id')

        # Deleting field 'basesection.secondary_menu_template'
        db.delete_column('section_basesection', 'secondary_menu_template')

        # Deleting field 'basesection.secondary_menu'
        db.delete_column('section_basesection', 'secondary_menu_id')

        # Deleting field 'basesection.interest_menu_template'
        db.delete_column('section_basesection', 'interest_menu_template')

        delete_south_trans_column(
            table='section_document',
            field_name='photo_description',
        )

        # Deleting field 'customstyle.searcher_right_arrow'
        db.delete_column('section_customstyle', 'searcher_right_arrow')

        # Deleting field 'customstyle.searcher_tab_image'
        db.delete_column('section_customstyle', 'searcher_tab_image')

        # Deleting field 'customstyle.content_head_background'
        db.delete_column('section_customstyle', 'content_head_background')

        # Deleting field 'customstyle.search_results_item_background'
        db.delete_column('section_customstyle', 'search_results_item_background')

        # Deleting field 'customstyle.searcher_last_tab_image'
        db.delete_column('section_customstyle', 'searcher_last_tab_image')

        # Deleting field 'customstyle.menu_head_background'
        db.delete_column('section_customstyle', 'menu_head_background')

        # Deleting field 'customstyle.menu_link_color'
        db.delete_column('section_customstyle', 'menu_link_color')

        # Deleting field 'customstyle.searcher_left_arrow'
        db.delete_column('section_customstyle', 'searcher_left_arrow')

        # Deleting field 'customstyle.color_3'
        db.delete_column('section_customstyle', 'color_3')

        # Deleting field 'customstyle.color_2'
        db.delete_column('section_customstyle', 'color_2')

        # Deleting field 'customstyle.color_1'
        db.delete_column('section_customstyle', 'color_1')


    def backwards(self, orm):

        # Adding field 'basesection.main_menu_template'
        db.add_column('section_basesection', 'main_menu_template', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'basesection.interest_menu'
        db.add_column('section_basesection', 'interest_menu', self.gf('django.db.models.fields.related.OneToOneField')(related_name='interest_menu_section', unique=True, null=True, to=orm['section.Menu'], blank=True), keep_default=False)

        # Adding field 'basesection.secondary_menu_template'
        db.add_column('section_basesection', 'secondary_menu_template', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'basesection.secondary_menu'
        db.add_column('section_basesection', 'secondary_menu', self.gf('django.db.models.fields.related.OneToOneField')(related_name='secondary_menu_section', unique=True, null=True, to=orm['section.Menu'], blank=True), keep_default=False)

        # Adding field 'basesection.interest_menu_template'
        db.add_column('section_basesection', 'interest_menu_template', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.searcher_right_arrow'
        db.add_column('section_customstyle', 'searcher_right_arrow', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.searcher_tab_image'
        db.add_column('section_customstyle', 'searcher_tab_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.content_head_background'
        db.add_column('section_customstyle', 'content_head_background', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.search_results_item_background'
        db.add_column('section_customstyle', 'search_results_item_background', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.searcher_last_tab_image'
        db.add_column('section_customstyle', 'searcher_last_tab_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.menu_head_background'
        db.add_column('section_customstyle', 'menu_head_background', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.menu_link_color'
        db.add_column('section_customstyle', 'menu_link_color', self.gf('cmsutils.db.fields.ColorField')(null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.searcher_left_arrow'
        db.add_column('section_customstyle', 'searcher_left_arrow', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.color_3'
        db.add_column('section_customstyle', 'color_3', self.gf('cmsutils.db.fields.ColorField')(null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.color_2'
        db.add_column('section_customstyle', 'color_2', self.gf('cmsutils.db.fields.ColorField')(null=True, blank=True), keep_default=False)

        # Adding field 'customstyle.color_1'
        db.add_column('section_customstyle', 'color_1', self.gf('cmsutils.db.fields.ColorField')(null=True, blank=True), keep_default=False)


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'Meta': {'object_name': 'BaseContent'},
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'commentable': ('django.db.models.fields.CharField', [], {'default': "'allowed'", 'max_length': '20'}),
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.ContactInfo']", 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            
            
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_autolocated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_editor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_edited_content'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Location']", 'null': 'True', 'blank': 'True'}),
            'main_image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'map_icon': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'meta_desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'multimedia': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.BaseMultimedia']", 'through': "'MultimediaRelation'", 'blank': 'True'}),
            
            
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'contents_owned'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            
            
            'rank': ('django.db.models.fields.FloatField', [], {'default': '100.0', 'db_index': 'True'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['base.BaseContent']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'unique': 'True', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
            'user_modification_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'base.contactinfo': {
            'Meta': {'object_name': 'ContactInfo'},
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'contact_email2': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'base.multimediarelation': {
            'Meta': {'unique_together': "(('content', 'multimedia'),)", 'object_name': 'MultimediaRelation'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'multimedia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multimedia.BaseMultimedia']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
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
            'tags': ('tagging.fields.TagField', [], {'default': "''"})
        },
        'multimedia.photo': {
            'Meta': {'object_name': 'Photo', '_ormbases': ['multimedia.BaseMultimedia']},
            'basemultimedia_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['multimedia.BaseMultimedia']", 'unique': 'True', 'primary_key': 'True'}),
            
            
            'image': ('stdimage.fields.StdImageField', [], {'max_length': '200'}),
            'plone_uid': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'places.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'registry.registereditem': {
            'Meta': {'object_name': 'RegisteredItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'config': ('merengue.registry.dbfields.ConfigField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'section.absolutelink': {
            'Meta': {'object_name': 'AbsoluteLink', '_ormbases': ['section.BaseLink']},
            'baselink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseLink']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'section.appsection': {
            'Meta': {'object_name': 'AppSection', '_ormbases': ['section.BaseSection']},
            'basesection_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseSection']", 'unique': 'True', 'primary_key': 'True'})
        },
        'section.baselink': {
            'Meta': {'object_name': 'BaseLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.Menu']", 'unique': 'True'})
        },
        'section.basesection': {
            'Meta': {'object_name': 'BaseSection'},
            'customstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.CustomStyle']", 'null': 'True', 'blank': 'True'}),
            
            
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_main_content'", 'blank': 'True', 'null': 'True', 'to': "orm['base.BaseContent']"}),
            'main_image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'main_menu': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'main_menu_section'", 'unique': 'True', 'null': 'True', 'to': "orm['section.Menu']"}),
            
            
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            
            
            'related_content': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['base.BaseContent']", 'through': "'SectionRelatedContent'"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'unique': 'True', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'})
        },
        'section.carousel': {
            'Meta': {'object_name': 'Carousel'},
            'class_name': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'photo_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.Photo']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'section.contentlink': {
            'Meta': {'object_name': 'ContentLink', '_ormbases': ['section.BaseLink']},
            'baselink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseLink']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"})
        },
        'section.customstyle': {
            'Meta': {'object_name': 'CustomStyle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'section.document': {
            'Meta': {'object_name': 'Document', '_ormbases': ['base.BaseContent']},
            'basecontent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['base.BaseContent']", 'unique': 'True', 'primary_key': 'True'}),
            'carousel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.Carousel']", 'null': 'True', 'blank': 'True'}),
            'floatimage': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'permanent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'photo': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'search_form': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'search_form_filters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'section.documentsection': {
            'Meta': {'object_name': 'DocumentSection'},
            
            
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': "orm['section.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {})
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
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'section.section': {
            'Meta': {'object_name': 'Section', '_ormbases': ['section.BaseSection']},
            'basesection_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseSection']", 'unique': 'True', 'primary_key': 'True'})
        },
        'section.sectionrelatedcontent': {
            'Meta': {'object_name': 'SectionRelatedContent', 'db_table': "'section_basesection_related_content'"},
            'basecontent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'basesection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['section.BaseSection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'section.viewletlink': {
            'Meta': {'object_name': 'ViewletLink', '_ormbases': ['section.BaseLink']},
            'baselink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['section.BaseLink']", 'unique': 'True', 'primary_key': 'True'}),
            'viewlet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['viewlet.RegisteredViewlet']"})
        },
        'viewlet.registeredviewlet': {
            'Meta': {'object_name': 'RegisteredViewlet', '_ormbases': ['registry.RegisteredItem']},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'registereditem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['registry.RegisteredItem']", 'unique': 'True', 'primary_key': 'True'})
        }
    }
    if not settings.USE_GIS:
        del models['places.location']
        del models['base.basecontent']['location']
        del models['base.basecontent']['map_icon']
        del models['base.basecontent']['is_autolocated']

    complete_apps = ['section']
