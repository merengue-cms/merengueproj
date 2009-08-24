from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from block.blocks import Block, ContentBlock
from plugins.news.models import NewsItem


class LatestNewsBlock(Block):
    name = 'latestnews'
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request):
        news_list = NewsItem.objects.published().order_by('-publish_date')
        return render_to_string('news/block_latest.html',
                                {'block_title': _('Latest news'),
                                 'news_list': news_list},
                                context_instance=RequestContext(request))


class NewsCommentsBlock(ContentBlock):
    name = 'newscomment'
    default_place = 'content'

    @classmethod
    def render(cls, request, content):
        return render_to_string('news/block_newscomments.html',
                                {'block_title': _('News comments'),
                                 'content': content},
                                context_instance=RequestContext(request))
