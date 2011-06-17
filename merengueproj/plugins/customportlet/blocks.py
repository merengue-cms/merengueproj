from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.block.blocks import Block

from plugins.customportlet.models import CustomPortlet


class CustomPortletBlock(Block):
    name = 'customportlet-block'
    default_place = 'homepage'
    verbose_name = _('Portlet block')
    help_text = _('Block that renders a custom portlet')

    def render(self, request, place, context, *args, **kwargs):
        customportlets = CustomPortlet.objects.all()

        return self.render_block(
            request, template_name='customportlet/block_pd.html',
            block_title=ugettext('Custom portlet'),
            context={'customportlets': customportlets})
