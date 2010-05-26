from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from merengue.block.blocks import Block
from plugins.standingout.models import StandingOut, StandingOutCategory


class StandingOutBlock(Block):
    name = 'standingout'
    default_place = 'rigthsidebar'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        standingout_categories = StandingOutCategory.objects.all()
        standingouts = None
        for standingout_category in standingout_categories:
            varible_value = context.get(standingout_category.context_variable, None)
            if varible_value:
                contenttype = ContentType.objects.get_for_model(varible_value)
                standingouts = StandingOut.objects.filter(related_id=varible_value.pk, related_content_type=contenttype)
                if standingouts:
                    break
        standingouts = standingouts or StandingOut.objects.filter(related_content_type__isnull=True, related_id__isnull=True)
        return cls.render_block(request, template_name='standingout/block_standingout.html',
                                block_title=_('Search'),
                                context={'standingouts': standingouts})
