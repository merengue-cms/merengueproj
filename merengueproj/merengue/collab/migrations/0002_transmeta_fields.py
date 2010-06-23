# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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
from merengue.collab.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'CollabCommentRevisorStatusType.label_fr'
        db.add_column('collab_collabcommentrevisorstatustype', 'label_fr', orm['collab.CollabCommentRevisorStatusType:label_fr'])
        
        # Adding field 'CollabCommentRevisorStatusType.label_en'
        db.add_column('collab_collabcommentrevisorstatustype', 'label_en', orm['collab.CollabCommentRevisorStatusType:label_en'])
        
        # Adding field 'CollabCommentUserType.label_es'
        db.rename_column('collab_collabcommentusertype', 'label', 'label_es')
        
        # Adding field 'CollabCommentUserType.label_fr'
        db.add_column('collab_collabcommentusertype', 'label_fr', orm['collab.CollabCommentUserType:label_fr'])
        
        # Adding field 'CollabCommentRevisorStatusType.reason_fr'
        db.add_column('collab_collabcommentrevisorstatustype', 'reason_fr', orm['collab.CollabCommentRevisorStatusType:reason_fr'])
        
        # Adding field 'CollabCommentRevisorStatusType.reason_en'
        db.add_column('collab_collabcommentrevisorstatustype', 'reason_en', orm['collab.CollabCommentRevisorStatusType:reason_en'])
        
        # Adding field 'CollabCommentUserType.label_en'
        db.add_column('collab_collabcommentusertype', 'label_en', orm['collab.CollabCommentUserType:label_en'])
        
        # Adding field 'CollabCommentRevisorStatusType.label_es'
        db.rename_column('collab_collabcommentrevisorstatustype', 'label', 'label_es')
        
        # Adding field 'CollabCommentRevisorStatusType.reason_es'
        db.rename_column('collab_collabcommentrevisorstatustype', 'reason', 'reason_es')
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'CollabCommentRevisorStatusType.label_fr'
        db.delete_column('collab_collabcommentrevisorstatustype', 'label_fr')
        
        # Deleting field 'CollabCommentRevisorStatusType.label_en'
        db.delete_column('collab_collabcommentrevisorstatustype', 'label_en')
        
        # Deleting field 'CollabCommentUserType.label_es'
        db.rename_column('collab_collabcommentusertype', 'label_es', 'label')
        
        # Deleting field 'CollabCommentUserType.label_fr'
        db.delete_column('collab_collabcommentusertype', 'label_fr')
        
        # Deleting field 'CollabCommentRevisorStatusType.reason_fr'
        db.delete_column('collab_collabcommentrevisorstatustype', 'reason_fr')
        
        # Deleting field 'CollabCommentRevisorStatusType.reason_en'
        db.delete_column('collab_collabcommentrevisorstatustype', 'reason_en')
        
        # Deleting field 'CollabCommentUserType.label_en'
        db.delete_column('collab_collabcommentusertype', 'label_en')
        
        # Deleting field 'CollabCommentRevisorStatusType.label_es'
        db.rename_column('collab_collabcommentrevisorstatustype', 'label_es', 'label')
        
        # Deleting field 'CollabCommentRevisorStatusType.reason_es'
        db.rename_column('collab_collabcommentrevisorstatustype', 'reason_es', 'reason')
        
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'collab.collabcomment': {
            'comment': ('django.db.models.fields.TextField', [], {}),
            'comment_user_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['collab.CollabCommentUserType']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_collabcomment'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'object_pk': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collabcomment_comments'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'user_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'collab.collabcommentrevisorstatus': {
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['collab.CollabComment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'auto_now_add': 'True', 'blank': 'True'}),
            'revisor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'revised_collabcommentrevisorstatus_comments'", 'null': 'True', 'to': "orm['auth.User']"}),
            'short_comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['collab.CollabCommentRevisorStatusType']"})
        },
        'collab.collabcommentrevisorstatustype': {
            'decorator': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'label_es': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'reason_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reason_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reason_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'default': "'just'", 'max_length': '30'})
        },
        'collab.collabcommentusertype': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'label_es': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['collab']
