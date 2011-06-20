from merengue.pluggable import Plugin

from plugins.fooplugin.actions import FooAction
from plugins.fooplugin.admin import FooModelAdmin, FooModelSectionAdmin
from plugins.fooplugin.blocks import FooBlock
from plugins.fooplugin.models import FooModel
from plugins.fooplugin.panels import FooPanel


class PluginConfig(Plugin):
    name = 'fooplugin'
    description = 'Foo plugin'
    version = '0.0.1a'

    url_prefixes = (
        ({'en': 'fooplugin', 'es': 'fooplugin-es'}, 'plugins.fooplugin.urls'),
    )

    def get_actions(self):
        return [FooAction]

    def get_blocks(self):
        return [FooBlock]

    def models(self):
        return [(FooModel, FooModelAdmin)]

    def section_models(self):
        return [(FooModel, FooModelSectionAdmin)]

    def get_perms(self):
        return (
            ('FooModel extra permission', 'foomodel_perm', [FooModel]),
        )

    def get_toolbar_panels(self):
        return [FooPanel]
