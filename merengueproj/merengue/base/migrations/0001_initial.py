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

# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from django.conf import settings
from merengue.base.models import *
from merengue.base.utils import south_trans_data, add_south_trans_fields

class Migration:
    
    def forwards(self, orm):
        # Adding model 'Location'
        if settings.USE_GIS:
            db.create_table('places_location', (
                ('id', orm['places.Location:id']),
                ('main_location', orm['places.Location:main_location']),
                ('address', orm['places.Location:address']),
                ('postal_code', orm['places.Location:postal_code']),
            ))
            db.send_create_signal('places', ['Location'])

        # Adding model 'ContactInfo'
        db.create_table('base_contactinfo', (
            ('id', orm['base.ContactInfo:id']),
            ('contact_email', orm['base.ContactInfo:contact_email']),
            ('contact_email2', orm['base.ContactInfo:contact_email2']),
            ('url', orm['base.ContactInfo:url']),
            ('phone', orm['base.ContactInfo:phone']),
            ('phone2', orm['base.ContactInfo:phone2']),
            ('fax', orm['base.ContactInfo:fax']),
        ))
        db.send_create_signal('base', ['ContactInfo'])

        # Adding model 'BaseContent'
        data = (('id', orm['base.BaseContent:id']),
                ('slug', orm['base.BaseContent:slug']),
                ('status', orm['base.BaseContent:status']),
                ('main_image', orm['base.BaseContent:main_image']),
                ('contact_info', orm['base.BaseContent:contact_info']),
                ('creation_date', orm['base.BaseContent:creation_date']),
                ('modification_date', orm['base.BaseContent:modification_date']),
                ('user_modification_date', orm['base.BaseContent:user_modification_date']),
                ('last_editor', orm['base.BaseContent:last_editor']),
                ('tags', orm['base.BaseContent:tags']),
                ('class_name', orm['base.BaseContent:class_name']),
                ('rank', orm['base.BaseContent:rank']))
        if settings.USE_GIS:
            gis_data = (('map_icon', orm['base.BaseContent:map_icon']),
                        ('is_autolocated', orm['base.BaseContent:is_autolocated']),
                        ('location', orm['base.BaseContent:location']))
            data = data + gis_data
        data = data + south_trans_data(
            orm=orm,
            trans_data={
                'base.BaseContent': ('name', 'description', 'plain_description', ),
            },
        )
        db.create_table('base_basecontent', data)
        db.send_create_signal('base', ['BaseContent'])

        # Adding model 'MultimediaRelation'
        db.create_table('base_multimediarelation', (
            ('id', orm['base.MultimediaRelation:id']),
            ('content', orm['base.MultimediaRelation:content']),
            ('multimedia', orm['base.MultimediaRelation:multimedia']),
            ('is_featured', orm['base.MultimediaRelation:is_featured']),
            ('order', orm['base.MultimediaRelation:order']),
        ))
        db.send_create_signal('base', ['MultimediaRelation'])

        # Adding ManyToManyField 'BaseContent.owners'
        db.create_table('base_basecontent_owners', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('basecontent', models.ForeignKey(orm.BaseContent, null=False)),
            ('user', models.ForeignKey(orm['auth.User'], null=False))
        ))

        # Adding ManyToManyField 'BaseContent.related_items'
        db.create_table('base_basecontent_related_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_basecontent', models.ForeignKey(orm.BaseContent, null=False)),
            ('to_basecontent', models.ForeignKey(orm.BaseContent, null=False))
        ))

        # Creating unique_together for [content, multimedia] on MultimediaRelation.
        db.create_unique('base_multimediarelation', ['content_id', 'multimedia_id'])


    def backwards(self, orm):

        # Deleting unique_together for [content, multimedia] on MultimediaRelation.
        db.delete_unique('base_multimediarelation', ['content_id', 'multimedia_id'])

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

        if settings.USE_GIS:
            # Deleting model 'Location'
            db.delete_table('places_location')

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
            'tags': ('TagField', [], {}),
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
        'base.multimediarelation': {
            'Meta': {'unique_together': "(('content', 'multimedia'),)"},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'multimedia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multimedia.BaseMultimedia']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'tags': ('TagField', [], {})
        },
        'places.location': {
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }
    add_south_trans_fields(models, {
        'base.basecontent': {
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plain_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
        },
    })

    if not settings.USE_GIS:
        del models['places.location']
        del models['base.basecontent']['location']
        del models['base.basecontent']['map_icon']
        del models['base.basecontent']['is_autolocated']

    complete_apps = ['base', 'places']
