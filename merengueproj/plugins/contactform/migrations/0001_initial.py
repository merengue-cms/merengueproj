# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from merengue.base.utils import table_exists, south_trans_data, add_south_trans_fields


class Migration(SchemaMigration):

    def forwards(self, orm):
        if table_exists('contactform_contactform'):
            return

        # Adding model 'ContactForm'
        contactform_data = (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('plugins.contactform.fields.ModelMultiEmailField')(default='webmaster@localhost')),
            ('bcc', self.gf('plugins.contactform.fields.ModelMultiEmailField')(blank=True)),
            ('redirect_to', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('subject_fixed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reset_button', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('captcha', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sender_email', self.gf('django.db.models.fields.BooleanField')(default=False)),
        )
        contactform_data = contactform_data + south_trans_data(
            orm=orm,
            trans_data={
                'contactform.ContactForm': ('description', 'sent_msg', 'reset_msg', 'submit_msg', 'subject', 'title', ),
            },
        )
        db.create_table('contactform_contactform', contactform_data)
        db.send_create_signal('contactform', ['ContactForm'])

        # Adding M2M table for field content on 'ContactForm'
        db.create_table('contactform_contactform_content', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contactform', models.ForeignKey(orm['contactform.contactform'], null=False)),
            ('basecontent', models.ForeignKey(orm['base.basecontent'], null=False))
        ))
        db.create_unique('contactform_contactform_content', ['contactform_id', 'basecontent_id'])

        # Adding model 'ContactFormOpt'
        contactform_contactformopt_data = (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contact_form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='opts', to=orm['contactform.ContactForm'])),
        )
        contactform_contactformopt_data = contactform_contactformopt_data + south_trans_data(
            orm=orm,
            trans_data={
                'contactform.ContactFormOpt': ('label', 'help_text', ),
            },
        )
        db.create_table('contactform_contactformopt', contactform_contactformopt_data)
        db.send_create_signal('contactform', ['ContactFormOpt'])

        # Adding model 'ContactFormSelectOpt'
        contactform_contactformselectopt_data = (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'choices', to=orm['contactform.ContactFormOpt'])),
        )
        contactform_contactformselectopt_data = contactform_contactformselectopt_data + south_trans_data(
            orm=orm,
            trans_data={
                'contactform.ContactFormSelectOpt': ('label', ),
            },
        )
        db.create_table('contactform_contactformselectopt', contactform_contactformselectopt_data)
        db.send_create_signal('contactform', ['ContactFormSelectOpt'])

        # Adding model 'SentContactForm'
        db.create_table('contactform_sentcontactform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact_form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contactform.ContactForm'])),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('sent_msg', self.gf('merengue.base.dbfields.JSONField')()),
            ('sent_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('contactform', ['SentContactForm'])

    def backwards(self, orm):

        # Deleting model 'ContactForm'
        db.delete_table('contactform_contactform')

        # Removing M2M table for field content on 'ContactForm'
        db.delete_table('contactform_contactform_content')

        # Deleting model 'ContactFormOpt'
        db.delete_table('contactform_contactformopt')

        # Deleting model 'ContactFormSelectOpt'
        db.delete_table('contactform_contactformselectopt')

        # Deleting model 'SentContactForm'
        db.delete_table('contactform_sentcontactform')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'base.basecontent': {
            'Meta': {'object_name': 'BaseContent'},
            'adquire_global_permissions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'commentable': ('django.db.models.fields.CharField', [], {'default': "'allowed'", 'max_length': '20'}),
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.ContactInfo']", 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'has_related_blocks': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_editor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_edited_content'", 'null': 'True', 'to': "orm['auth.User']"}),
            'main_image': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'map_icon': ('stdimage.fields.StdImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'meta_desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'multimedia': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['multimedia.BaseMultimedia']", 'symmetrical': 'False', 'through': "orm['base.MultimediaRelation']", 'blank': 'True'}),
            'no_changeable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_changeable_fields': ('merengue.base.dbfields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'no_deletable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contents_owned'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contents_participated'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'rank': ('django.db.models.fields.FloatField', [], {'default': '100.0', 'db_index': 'True'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['base.BaseContent']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'user_modification_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'workflow_status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.State']", 'null': 'True', 'blank': 'True'})
        },
        'base.contactinfo': {
            'Meta': {'object_name': 'ContactInfo'},
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'contact_email2': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'base.multimediarelation': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('content', 'multimedia'),)", 'object_name': 'MultimediaRelation'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BaseContent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multimedia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multimedia.BaseMultimedia']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'contactform.contactform': {
            'Meta': {'object_name': 'ContactForm'},
            'bcc': ('plugins.contactform.fields.ModelMultiEmailField', [], {'blank': 'True'}),
            'captcha': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'content': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contact_form'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['base.BaseContent']"}),
            'email': ('plugins.contactform.fields.ModelMultiEmailField', [], {'default': "'webmaster@localhost'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redirect_to': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'reset_button': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sender_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_fixed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
        },
        'contactform.contactformopt': {
            'Meta': {'ordering': "('order',)", 'object_name': 'ContactFormOpt'},
            'contact_form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'opts'", 'to': "orm['contactform.ContactForm']"}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'contactform.contactformselectopt': {
            'Meta': {'object_name': 'ContactFormSelectOpt'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'choices'", 'to': "orm['contactform.ContactFormOpt']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'contactform.sentcontactform': {
            'Meta': {'object_name': 'SentContactForm'},
            'contact_form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contactform.ContactForm']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sent_msg': ('merengue.base.dbfields.JSONField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
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
            'tags': ('tagging.fields.TagField', [], {})
        },
        'perms.permission': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Permission'},
            'builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'content_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'content_types'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'workflow.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'transitions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'states'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['workflow.Transition']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'states'", 'to': "orm['workflow.Workflow']"})
        },
        'workflow.transition': {
            'Meta': {'object_name': 'Transition'},
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'destination_state'", 'null': 'True', 'to': "orm['workflow.State']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['perms.Permission']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transitions'", 'to': "orm['workflow.Workflow']"})
        },
        'workflow.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_state': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'workflow_state'", 'null': 'True', 'to': "orm['workflow.State']"}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['perms.Permission']", 'through': "orm['workflow.WorkflowPermissionRelation']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'workflow.workflowpermissionrelation': {
            'Meta': {'unique_together': "(('workflow', 'permission'),)", 'object_name': 'WorkflowPermissionRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permissions'", 'to': "orm['perms.Permission']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.Workflow']"})
        }
    }
    add_south_trans_fields(models, {
        'contactform.contactform': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sent_msg': ('django.db.models.fields.TextField', [], {'default': "u'The form was sent correctly'", 'blank': 'True'}),
            'reset_msg': ('django.db.models.fields.CharField', [], {'default': "u'Reset'", 'max_length': '200', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "u'Subject'", 'max_length': '200', 'blank': 'True'}),
            'submit_msg': ('django.db.models.fields.CharField', [], {'default': "u'Send'", 'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
        },
        'contactform.contactformopt': {
            'help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
        },
        'contactform.contactformselectopt': {
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
        },
    })

    complete_apps = ['contactform']
