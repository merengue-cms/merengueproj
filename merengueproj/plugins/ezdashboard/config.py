from django.utils.translation import ugettext_lazy as _

from merengue.plugins import Plugin
from merengue.registry import params


class PluginConfig(Plugin):
    name = 'EzDashboard'
    description = 'Dashboard for users plugins like iGoogle, based on EzWeb platform'
    version = '0.0.1a'
    url_prefixes = (
        ('dashboard', 'plugins.ezdashboard.urls'),
    )
    config_params = [
        params.Single(name='theme', label=_('EzWeb theme'), default='default'),
        params.Single(name='ezweburl', label=_('EzWeb base URL'), default='http://ezweb.yaco.es/'),
    ]

    #@classmethod
    #def get_blocks(cls):
        #return [LatestNewsBlock, NewsCommentsBlock]
