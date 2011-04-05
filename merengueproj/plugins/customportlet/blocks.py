from django.utils.translation import ugettext as _

from merengue.block.blocks import Block

from plugins.customportlet.models import CustomPortlet


class CustomPortletBlock(Block):
    name = 'customportlet-block'
    default_place = 'homepage'

    def render(self, request, place, context, *args, **kwargs):
        customportlets = CustomPortlet.objects.all()

        return self.render_block(
            request, template_name='customportlet/block_pd.html',
            block_title=_('Custom portlet'),
            context={'customportlets': customportlets})
