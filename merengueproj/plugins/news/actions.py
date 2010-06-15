from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import SiteAction


class NewsIndex(SiteAction):
    name = 'newsindex'
    verbose_name = _('News index')

    @classmethod
    def get_response(cls, request):
        return HttpResponseRedirect(reverse('news_index'))


class NewsRSS(SiteAction):
    name = 'newsrss'
    verbose_name = _('News rss')

    @classmethod
    def get_response(cls, request):
        return HttpResponseRedirect(reverse('news_index'))
