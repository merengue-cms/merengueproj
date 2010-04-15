
from south.db import db
from django.db import models
from merengue.places.models import *

class Migration:
    
    def forwards(self, orm):
        pass # merengue.places models are added in merengue.base migrations
    
    
    def backwards(self, orm):
        pass # merengue.places models are deleted in merengue.base migrations
        # Deleting model 'Location'
    
    models = {
        'places.location': {
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'borders': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['places']
