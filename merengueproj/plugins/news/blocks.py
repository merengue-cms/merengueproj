from django.utils.translation import ugettext as _

from merengue.block.blocks import Block, ContentBlock
from plugins.news.views import get_news


class LatestNewsBlock(Block):
    name = 'latestnews'
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        news_list = get_news(request, 5)
        return cls.render_block(request, template_name='news/block_latest.html',
                                block_title=_('Latest news'),
                                context={'news_list': news_list})


class NewsCommentsBlock(ContentBlock):
    name = 'newscomment'
    default_place = 'aftercontent'

    @classmethod
    def render(cls, request, place, content, context, *args, **kwargs):
        return cls.render_block(request, template_name='news/block_newscomments.html',
                                block_title=_('News comments'),
                                context={'content': content})
