# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Workflow'
        db.create_table('workflow_workflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('initial_state', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='workflow_state', null=True, to=orm['workflow.State'])),
        ))
        db.send_create_signal('workflow', ['Workflow'])

        # Adding model 'State'
        db.create_table('workflow_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(related_name='states', to=orm['workflow.Workflow'])),
        ))
        db.send_create_signal('workflow', ['State'])

        # Adding M2M table for field transitions on 'State'
        db.create_table('workflow_state_transitions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('state', models.ForeignKey(orm['workflow.state'], null=False)),
            ('transition', models.ForeignKey(orm['workflow.transition'], null=False))
        ))
        db.create_unique('workflow_state_transitions', ['state_id', 'transition_id'])

        # Adding model 'Transition'
        db.create_table('workflow_transition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transitions', to=orm['workflow.Workflow'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='destination_state', null=True, to=orm['workflow.State'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['perms.Permission'], null=True, blank=True)),
        ))
        db.send_create_signal('workflow', ['Transition'])

        # Adding model 'WorkflowModelRelation'
        db.create_table('workflow_workflowmodelrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], unique=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wmrs', to=orm['workflow.Workflow'])),
        ))
        db.send_create_signal('workflow', ['WorkflowModelRelation'])

        # Adding model 'WorkflowPermissionRelation'
        db.create_table('workflow_workflowpermissionrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workflow.Workflow'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='permissions', to=orm['perms.Permission'])),
        ))
        db.send_create_signal('workflow', ['WorkflowPermissionRelation'])

        # Adding unique constraint on 'WorkflowPermissionRelation', fields ['workflow', 'permission']
        db.create_unique('workflow_workflowpermissionrelation', ['workflow_id', 'permission_id'])

        # Adding model 'StateInheritanceBlock'
        db.create_table('workflow_stateinheritanceblock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workflow.State'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['perms.Permission'])),
        ))
        db.send_create_signal('workflow', ['StateInheritanceBlock'])

        # Adding model 'StatePermissionRelation'
        db.create_table('workflow_statepermissionrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workflow.State'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['perms.Permission'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['perms.Role'])),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'perms.permission': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Permission'},
            'builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'content_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'content_types'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'perms.role': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        'workflow.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'transitions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'states'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['workflow.Transition']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'states'", 'to': "orm['workflow.Workflow']"})
        },
        'workflow.stateinheritanceblock': {
            'Meta': {'object_name': 'StateInheritanceBlock'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Permission']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.State']"})
        },
        'workflow.statepermissionrelation': {
            'Meta': {'object_name': 'StatePermissionRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Permission']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Role']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.State']"})
        },
        'workflow.transition': {
            'Meta': {'object_name': 'Transition'},
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'destination_state'", 'null': 'True', 'to': "orm['workflow.State']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Permission']", 'null': 'True', 'blank': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transitions'", 'to': "orm['workflow.Workflow']"})
        },
        'workflow.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_state': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'workflow_state'", 'null': 'True', 'to': "orm['workflow.State']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['perms.Permission']", 'through': "'WorkflowPermissionRelation'", 'symmetrical': 'False'})
        },
        'workflow.workflowmodelrelation': {
            'Meta': {'object_name': 'WorkflowModelRelation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wmrs'", 'to': "orm['workflow.Workflow']"})
        },
        'workflow.workflowpermissionrelation': {
            'Meta': {'unique_together': "(('workflow', 'permission'),)", 'object_name': 'WorkflowPermissionRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permissions'", 'to': "orm['perms.Permission']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.Workflow']"})
        }
    }

    complete_apps = ['workflow']
