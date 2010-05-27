# encoding: utf-8
from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        from oembed.models import ProviderRule

        try:
            rule = ProviderRule.objects.get(name='YouTube (OohEmbed)')
            rule.name='YouTube'
            rule.endpoint='http://www.youtube.com/oembed'
            rule.save()
        except ProviderRule.DoesNotExist:
            pass

    def backwards(self, orm):
        "Write your backwards methods here."
