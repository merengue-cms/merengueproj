# -*- encoding: utf-8 -*-

# Copyright (c) 2011 by Yaco Sistemas
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
from south.v2 import SchemaMigration
from django.db import models

from merengue.base.utils import south_trans_data, add_south_trans_fields


class Migration(SchemaMigration):

    depends_on = (
        ("perms", "0001_initial"),
     )

    def forwards(self, orm):
        # Adding model 'Workflow'
        data = (('id', orm['workflow.Workflow:id']),
                ('slug', orm['workflow.Workflow:slug']),
                ('initial_state', orm['workflow.Workflow:initial_state']))
        data = data + south_trans_data(
            orm=orm,
            trans_data={
                'workflow.Workflow': ('name', ),
            },
        )
        db.create_table('workflow_workflow', data)
        db.send_create_signal('workflow', ['Workflow'])

        # Adding model 'State'
        data = (('id', orm['workflow.State:id']),
                ('slug', orm['workflow.State:slug']),
                ('workflow', orm['workflow.State:workflow']))
        data = data + south_trans_data(
            orm=orm,
            trans_data={
                'workflow.State': ('name', ),
            },
        )
        db.create_table('workflow_state', data)
        db.send_create_signal('workflow', ['State'])

        # Adding M2M table for field transitions on 'State'
        db.create_table('workflow_state_transitions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('state', models.ForeignKey(orm['workflow.state'], null=False)),
            ('transition', models.ForeignKey(orm['workflow.transition'], null=False))
        ))
        db.create_unique('workflow_state_transitions', ['state_id', 'transition_id'])

        # Adding model 'Transition'
        data = (('id', orm['workflow.Transition:id']),
                ('slug', orm['workflow.Transition:slug']),
                ('workflow', orm['workflow.Transition:workflow']),
                ('destination', orm['workflow.Transition:destination']),
                ('permission', orm['workflow.Transition:permission']))
        data = data + south_trans_data(
            orm=orm,
            trans_data={
                'workflow.Transition': ('name', ),
            },
        )
        db.create_table('workflow_transition', data)
        db.send_create_signal('workflow', ['Transition'])

        # Adding model 'WorkflowModelRelation'
        db.create_table('workflow_workflowmodelrelation', (
            ('id', orm['workflow.WorkflowModelRelation:id']),
            ('content_type', orm['workflow.WorkflowModelRelation:content_type']),
            ('workflow', orm['workflow.WorkflowModelRelation:workflow']),
        ))
        db.send_create_signal('workflow', ['WorkflowModelRelation'])

        # Adding model 'WorkflowPermissionRelation'
        db.create_table('workflow_workflowpermissionrelation', (
            ('id', orm['workflow.WorkflowPermissionRelation:id']),
            ('workflow', orm['workflow.WorkflowPermissionRelation:workflow']),
            ('permission', orm['workflow.WorkflowPermissionRelation:permission']),
        ))
        db.send_create_signal('workflow', ['WorkflowPermissionRelation'])

        # Adding unique constraint on 'WorkflowPermissionRelation', fields ['workflow', 'permission']
        db.create_unique('workflow_workflowpermissionrelation', ['workflow_id', 'permission_id'])

        # Adding model 'StateInheritanceBlock'
        db.create_table('workflow_stateinheritanceblock', (
            ('id', orm['workflow.StateInheritanceBlock:id']),
            ('state', orm['workflow.StateInheritanceBlock:state']),
            ('permission', orm['workflow.StateInheritanceBlock:permission']),
        ))
        db.send_create_signal('workflow', ['StateInheritanceBlock'])

        # Adding model 'StatePermissionRelation'
        db.create_table('workflow_statepermissionrelation', (
            ('id', orm['workflow.StatePermissionRelation:id']),
            ('state', orm['workflow.StatePermissionRelation:state']),
            ('permission', orm['workflow.StatePermissionRelation:permission']),
            ('role', orm['workflow.StatePermissionRelation:role']),
        ))
        db.send_create_signal('workflow', ['StatePermissionRelation'])

    def backwards(self, orm):
        # Removing unique constraint on 'WorkflowPermissionRelation', fields ['workflow', 'permission']
        db.delete_unique('workflow_workflowpermissionrelation', ['workflow_id', 'permission_id'])

        # Deleting model 'Workflow'
        db.delete_table('workflow_workflow')

        # Deleting model 'State'
        db.delete_table('workflow_state')

        # Removing M2M table for field transitions on 'State'
        db.delete_table('workflow_state_transitions')

        # Deleting model 'Transition'
        db.delete_table('workflow_transition')

        # Deleting model 'WorkflowModelRelation'
        db.delete_table('workflow_workflowmodelrelation')

        # Deleting model 'WorkflowPermissionRelation'
        db.delete_table('workflow_workflowpermissionrelation')

        # Deleting model 'StateInheritanceBlock'
        db.delete_table('workflow_stateinheritanceblock')

        # Deleting model 'StatePermissionRelation'
        db.delete_table('workflow_statepermissionrelation')

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
        },
        'perms.permission': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Permission'},
            'builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'content_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'content_types'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
        },
        'perms.role': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
        },
        'workflow.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'transitions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'states'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['workflow.Transition']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'states'", 'to': "orm['workflow.Workflow']"}),
        },
        'workflow.stateinheritanceblock': {
            'Meta': {'object_name': 'StateInheritanceBlock'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Permission']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.State']"}),
        },
        'workflow.statepermissionrelation': {
            'Meta': {'object_name': 'StatePermissionRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Permission']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Role']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.State']"}),
        },
        'workflow.transition': {
            'Meta': {'object_name': 'Transition'},
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'destination_state'", 'null': 'True', 'to': "orm['workflow.State']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Permission']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transitions'", 'to': "orm['workflow.Workflow']"}),
        },
        'workflow.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_state': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'workflow_state'", 'null': 'True', 'to': "orm['workflow.State']"}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['perms.Permission']", 'through': "'WorkflowPermissionRelation'", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
        },
        'workflow.workflowmodelrelation': {
            'Meta': {'object_name': 'WorkflowModelRelation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wmrs'", 'to': "orm['workflow.Workflow']"}),
        },
        'workflow.workflowpermissionrelation': {
            'Meta': {'unique_together': "(('workflow', 'permission'),)", 'object_name': 'WorkflowPermissionRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permissions'", 'to': "orm['perms.Permission']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.Workflow']"}),
        }
    }
    add_south_trans_fields(models, {
        'workflow.workflow': {
            'name': ('django.db.models.fields.CharField', [],
                     {'db_index': 'True', 'max_length': '200'}),
        },
        'workflow.state': {
            'name': ('django.db.models.fields.CharField', [],
                     {'db_index': 'True', 'max_length': '200'}),
        },
        'workflow.transition': {
            'name': ('django.db.models.fields.CharField', [],
                     {'db_index': 'True', 'max_length': '200'}),
        },
    })

    complete_apps = ['workflow']
