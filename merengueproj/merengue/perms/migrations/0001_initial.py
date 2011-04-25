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
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db import connection
from django.conf import settings


class Migration(SchemaMigration):

    depends_on = (
        ("base", "0001_initial"),
     )

    def forwards(self, orm):
        from south.models import MigrationHistory
        if 'perms_permission' in connection.introspection.table_names():
            MigrationHistory.objects.create(
                app_name='perms', migration='0001_initial', applied=datetime.datetime.now(),
            )
            return

        # Adding model 'Permission'
        db.create_table('perms_permission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True)),
            ('codename', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True)),
            ('builtin', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('perms', ['Permission'])

        # Adding M2M table for field content_types on 'Permission'
        db.create_table('perms_permission_content_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('permission', models.ForeignKey(orm['perms.permission'], null=False)),
            ('contenttype', models.ForeignKey(orm['contenttypes.contenttype'], null=False))
        ))
        db.create_unique('perms_permission_content_types', ['permission_id', 'contenttype_id'])

        # Adding model 'ObjectPermission'
        db.create_table('perms_objectpermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['perms.Role'], null=True, blank=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['perms.Permission'])),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.BaseContent'])),
        ))
        db.send_create_signal('perms', ['ObjectPermission'])

        # Adding model 'ObjectPermissionInheritanceBlock'
        db.create_table('perms_objectpermissioninheritanceblock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['perms.Permission'])),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.BaseContent'])),
        ))
        db.send_create_signal('perms', ['ObjectPermissionInheritanceBlock'])

        # Adding model 'Role'
        db.create_table('perms_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True)),
        ))
        db.send_create_signal('perms', ['Role'])

        # Adding model 'PrincipalRoleRelation'
        db.create_table('perms_principalrolerelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, blank=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['perms.Role'])),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.BaseContent'], null=True, blank=True)),
        ))
        db.send_create_signal('perms', ['PrincipalRoleRelation'])

    def backwards(self, orm):

        # Deleting model 'Permission'
        db.delete_table('perms_permission')

        # Removing M2M table for field content_types on 'Permission'
        db.delete_table('perms_permission_content_types')

        # Deleting model 'ObjectPermission'
        db.delete_table('perms_objectpermission')

        # Deleting model 'ObjectPermissionInheritanceBlock'
        db.delete_table('perms_objectpermissioninheritanceblock')

        # Deleting model 'Role'
        db.delete_table('perms_role')

        # Deleting model 'PrincipalRoleRelation'
        db.delete_table('perms_principalrolerelation')

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
        'perms.objectpermission': {
            'Meta': {'object_name': 'ObjectPermission'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Permission']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Role']", 'null': 'True', 'blank': 'True'})
        },
        'perms.objectpermissioninheritanceblock': {
            'Meta': {'object_name': 'ObjectPermissionInheritanceBlock'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Permission']"})
        },
        'perms.permission': {
            'Meta': {'object_name': 'Permission'},
            'builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'content_types': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'content_types'", 'blank': 'True', 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'})
        },
        'perms.principalrolerelation': {
            'Meta': {'object_name': 'PrincipalRoleRelation'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'perms.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'})
        },
        'places.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    if not settings.USE_GIS:
        del models['places.location']
        del models['base.basecontent']['location']
        del models['base.basecontent']['map_icon']

    complete_apps = ['perms']
