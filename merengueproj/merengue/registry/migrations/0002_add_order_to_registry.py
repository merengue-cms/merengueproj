
from south.db import db
from django.db import models
from merengue.registry.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'RegisteredItem.order'
        db.add_column('registry_registereditem', 'order', orm['registry.registereditem:order'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'RegisteredItem.order'
        db.delete_column('registry_registereditem', 'order')
        
    
    
    models = {
        'registry.registereditem': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'config': ('ConfigField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['registry']
