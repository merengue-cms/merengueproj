# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

from merengue.base.utils import table_exists


class Migration(SchemaMigration):

    def forwards(self, orm):
        if table_exists('review_reviewtask'):
            return  # already migrated

        # Adding model 'ReviewTask'
        db.create_table('review_reviewtask', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_by', to=orm['auth.User'])),
            ('assigned_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assigned_to', to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('is_done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('task_object_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='review_tasks', null=True, to=orm['contenttypes.ContentType'])),
            ('task_object_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('review', ['ReviewTask'])

    def backwards(self, orm):

        # Deleting model 'ReviewTask'
        db.delete_table('review_reviewtask')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})},
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})},
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})},
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})},
        'review.reviewtask': {
            'Meta': {'ordering': "('is_done', 'title', 'url', 'owner', 'assigned_to')", 'object_name': 'ReviewTask'},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assigned_to'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_by'", 'to': "orm['auth.User']"}),
            'task_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'task_object_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'review_tasks'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'})}}

    complete_apps = ['review']
