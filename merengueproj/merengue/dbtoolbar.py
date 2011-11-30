from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from debug_toolbar.panels import DebugPanel

from merengue.block.blocks import block_debug_info


class BlockDebugPanel(DebugPanel):
    """
    Panel that displays information about the blocks while processing
    the request.
    """
    name = 'Blocks'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._blocks = []

    def nav_title(self):
        return _('Blocks')

    def title(self):
        return _('Blocks information')

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        block_info = block_debug_info.values()
        block_info.sort(key=lambda x: x['time'])
        block_info.reverse()
        context.update({
            'block_info': block_info,
        })

        return render_to_string('dbtoolbar/block_panel.html', context)
