from django.utils.translation import ugettext as _

from block.blocks import Block, ContentBlock
from plugins.news.models import NewsItem


class LatestNewsBlock(Block):
    name = 'latestnews'
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request):
        news_list = NewsItem.objects.published().order_by('-publish_date')
        return cls.render_block(request, template_name='news/block_latest.html',
                                block_title=_('Latest news'),
                                context={'news_list': news_list})


class NewsCommentsBlock(ContentBlock):
    name = 'newscomment'
    default_place = 'content'

    @classmethod
    def render(cls, request, content):
        return cls.render_block(request, template_name='news/block_newscomments.html',
                                block_title=_('News comments'),
                                context={'content': content})
