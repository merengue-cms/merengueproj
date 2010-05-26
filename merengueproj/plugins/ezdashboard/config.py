from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params


class PluginConfig(Plugin):
    name = 'EzDashboard'
    description = 'Dashboard for users plugins like iGoogle, based on ' \
                  'EzWeb platform'
    version = '0.0.2a'
    url_prefixes = (
        ('dashboard', 'plugins.ezdashboard.urls'),
    )
    required_apps = ('django.contrib.sites', )
    config_params = [
        params.Single(name='theme', label=_('EzWeb theme'), default='default'),
        params.Single(name='url', label=_('EzWeb base URL'),
                      default='http://ezweb.yaco.es/'),
        params.Single(name='style', label=_('EzWeb iframe CSS style'),
                      default='border: none;'),
        params.Single(name='class', label=_('EzWeb iframe CSS class'),
                      default=''),
        params.Single(name='width', label=_('EzWeb iframe width'),
                      default='100%'),
        params.Single(name='height', label=_('EzWeb iframe height'),
                      default='500px'),
        params.Single(name='lite', label=_('EzWeb lite'),
                      default=True),
    ]

    #@classmethod
    #def get_blocks(cls):
        #return [LatestNewsBlock, NewsCommentsBlock]
