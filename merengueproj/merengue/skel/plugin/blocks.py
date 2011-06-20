from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.block.blocks import Block
from merengue.registry import params

from plugins.fooplugin.models import FooModel


class FooBlock(Block):
    name = 'fooblock'
    verbose_name = _('Foo block')
    help_text = _('Block with last foo items published')
    default_place = 'leftsidebar'

    config_params = Block.config_params + [
        params.PositiveInteger(
            name='limit',
            label=_('number of foo items for the "Foo block" block'),
            default=3,
        ),
    ]

    default_caching_params = {
        'enabled': False,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': False,
        'vary_on_language': True,
    }

    def render(self, request, place, context, *args, **kwargs):
        limit = self.get_config().get('limit').get_value()
        content_list = FooModel.objects.published()[:limit]
        return self.render_block(request, template_name='foo_block.html',
                                 block_title=ugettext('Latest foo items'),
                                 context={'content_list': content_list})
