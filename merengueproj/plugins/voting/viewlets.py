from django.utils.translation import ugettext as _

from cmsutils.adminfilters import QueryStringManager

from merengue.base.models import BaseContent
from merengue.base.utils import copy_request
from merengue.viewlet.viewlets import Viewlet
from plugins.voting.models import Vote


def get_content_with_votes(request=None, limit=0, order_by='id'):
    votes = Vote.objects.all()
    contents = BaseContent.objects.published().filter(vote__in=votes)
    from copy import copy
    request_copy = copy_request(request, ['set_language'], copy)
    qsm = QueryStringManager(request, page_var='page')
    filters = qsm.get_filters()
    contents = contents.filter(**filters).distinct().select_related('votes').order_by(order_by)
    if limit:
        return contents[:limit]
    return contents


class BaseContentTopRated(Viewlet):
    name = 'basecontenttoprated'
    label = _('Content top rated')

    @classmethod
    def render(cls, request):
        votes_list = get_content_with_votes(request, limit=None, order_by='-vote__vote')
        return cls.render_viewlet(request, template_name='voting/viewlet_voting_basecontent.html',
                                  context={'votes_list': votes_list})


class BaseContentWithMoreVotes(Viewlet):
    name = 'basecontentwithmorevotes'
    label = _('Content with more votes')

    @classmethod
    def render(cls, request):
        votes_list = get_content_with_votes(request, limit=None, order_by='-vote__num_votes')
        return cls.render_viewlet(request, template_name='voting/viewlet_voting_basecontent.html',
                                  context={'votes_list': votes_list})
