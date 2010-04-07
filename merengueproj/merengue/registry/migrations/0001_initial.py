
from south.db import db
from django.db import models
from merengue.registry.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'RegisteredItem'
        db.create_table('registry_registereditem', (
            ('id', orm['registry.RegisteredItem:id']),
            ('class_name', orm['registry.RegisteredItem:class_name']),
            ('module', orm['registry.RegisteredItem:module']),
            ('category', orm['registry.RegisteredItem:category']),
            ('active', orm['registry.RegisteredItem:active']),
            ('config', orm['registry.RegisteredItem:config']),
        ))
        db.send_create_signal('registry', ['RegisteredItem'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'RegisteredItem'
        db.delete_table('registry_registereditem')
        
    
    
    models = {
        'registry.registereditem': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'config': ('ConfigField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        }
    }
    
    complete_apps = ['registry']
