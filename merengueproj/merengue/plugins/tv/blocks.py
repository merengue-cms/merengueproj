from django.utils.translation import ugettext as _

from merengue.block.blocks import Block
from plugins.tv.models import VideoStreaming


class LatestVideoBlock(Block):
    name = 'latestVideo'
    default_place = 'rightsidebar'

    @classmethod
    def render(cls, request, channel, context, *args, **kwargs):
        video_list = VideoStreaming.objects.all()
        return cls.render_block(request, template_name='tv/block_latest.html',
                                block_title=_('Latest video'),
                                context={'video_list': video_list})
