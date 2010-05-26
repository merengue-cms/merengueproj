from django.utils.translation import ugettext as _

from merengue.block.blocks import Block


class GoogleSearchBlock(Block):
    name = 'googlesearch'
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        from plugins.googlesearch.config import PluginConfig
        return cls.render_block(request, template_name='googlesearch/block_googlesearch.html',
                                block_title=_('Search'),
                                context={'plugin_config': PluginConfig.get_config()})
