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
from merengue.multimedia.models import *
from merengue.base.utils import south_trans_data, add_south_trans_fields


class Migration:

    def forwards(self, orm):

        # Adding model 'Photo'
        fields = (
            ('basemultimedia_ptr', orm['multimedia.Photo:basemultimedia_ptr']),
            ('image', orm['multimedia.Photo:image']),
            ('plone_uid', orm['multimedia.Photo:plone_uid']),
        )
        fields += south_trans_data(
            orm=orm,
            trans_data={
                'multimedia.photo': ('caption', ),
            },
        )
        db.create_table('multimedia_photo', fields)
        db.send_create_signal('multimedia', ['Photo'])

        # Adding model 'PanoramicView'
        db.create_table('multimedia_panoramicview', (
            ('basemultimedia_ptr', orm['multimedia.PanoramicView:basemultimedia_ptr']),
            ('preview', orm['multimedia.PanoramicView:preview']),
            ('external_url', orm['multimedia.PanoramicView:external_url']),
        ))
        db.send_create_signal('multimedia', ['PanoramicView'])

        # Adding model 'BaseMultimedia'
        db.create_table('multimedia_basemultimedia', (
            ('id', orm['multimedia.BaseMultimedia:id']),
            ('name', orm['multimedia.BaseMultimedia:name']),
            ('original_filename', orm['multimedia.BaseMultimedia:original_filename']),
            ('creation_date', orm['multimedia.BaseMultimedia:creation_date']),
            ('tags', orm['multimedia.BaseMultimedia:tags']),
            ('class_name', orm['multimedia.BaseMultimedia:class_name']),
            ('status', orm['multimedia.BaseMultimedia:status']),
            ('last_editor', orm['multimedia.BaseMultimedia:last_editor']),
            ('authors', orm['multimedia.BaseMultimedia:authors']),
        ))
        db.send_create_signal('multimedia', ['BaseMultimedia'])

        # Adding model 'Video'
        db.create_table('multimedia_video', (
            ('basemultimedia_ptr', orm['multimedia.Video:basemultimedia_ptr']),
            ('file', orm['multimedia.Video:file']),
            ('preview', orm['multimedia.Video:preview']),
            ('external_url', orm['multimedia.Video:external_url']),
            ('plone_uid', orm['multimedia.Video:plone_uid']),
        ))
        db.send_create_signal('multimedia', ['Video'])

        # Adding model 'Audio'
        db.create_table('multimedia_audio', (
            ('basemultimedia_ptr', orm['multimedia.Audio:basemultimedia_ptr']),
            ('file', orm['multimedia.Audio:file']),
        ))
        db.send_create_signal('multimedia', ['Audio'])

        # Adding model 'Image3D'
        db.create_table('multimedia_image3d', (
            ('basemultimedia_ptr', orm['multimedia.Image3D:basemultimedia_ptr']),
            ('file', orm['multimedia.Image3D:file']),
        ))
        db.send_create_signal('multimedia', ['Image3D'])


    def backwards(self, orm):

        # Deleting model 'Photo'
        db.delete_table('multimedia_photo')

        # Deleting model 'PanoramicView'
        db.delete_table('multimedia_panoramicview')

        # Deleting model 'BaseMultimedia'
        db.delete_table('multimedia_basemultimedia')

        # Deleting model 'Video'
        db.delete_table('multimedia_video')

        # Deleting model 'Audio'
        db.delete_table('multimedia_audio')

        # Deleting model 'Image3D'
        db.delete_table('multimedia_image3d')


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
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'multimedia.audio': {
            'basemultimedia_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['multimedia.BaseMultimedia']", 'unique': 'True', 'primary_key': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '200'})
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
        'multimedia.image3d': {
            'basemultimedia_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['multimedia.BaseMultimedia']", 'unique': 'True', 'primary_key': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'multimedia.panoramicview': {
            'basemultimedia_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['multimedia.BaseMultimedia']", 'unique': 'True', 'primary_key': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'preview': ('StdImageField', [], {'thumbnail_size': '(200,200)', 'max_length': '255', 'blank': 'True', 'null': 'True'})
        },
        'multimedia.photo': {
            'basemultimedia_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['multimedia.BaseMultimedia']", 'unique': 'True', 'primary_key': 'True'}),
            'image': ('StdImageField', [], {'max_length': '200', 'thumbnail_size': '(200,200)'}),
            'plone_uid': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'multimedia.video': {
            'basemultimedia_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['multimedia.BaseMultimedia']", 'unique': 'True', 'primary_key': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'plone_uid': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'preview': ('StdImageField', [], {'null': 'True', 'thumbnail_size': '(200,200)', 'blank': 'True'})
        }
    }
    add_south_trans_fields(models, {
        'multimedia.photo': {
            'caption': ('django.db.models.fields.TextField', [], {}),
        }
    })
    complete_apps = ['multimedia']
