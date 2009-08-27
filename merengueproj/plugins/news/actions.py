from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import SiteAction, ContentAction
from merengue.registry import params


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


class PDFExport(ContentAction):
    name = 'pdfexport'
    verbose_name = _('Export to PDF')
    config_params = [
        params.Single(name='username', label=_('username'), default='pepe'),
        params.Single(name='bestfriend', label=_('bestfriend'),
                      default='juan'),
        params.List(name='friends', label=_('friends'),
                    default=['antonio', 'juan'],
                    choices=[('antonio', 'Antonio'),
                             ('paco', 'Paco'),
                             ('rosa', 'Rosa'),
                             ('juan', 'Juan')]),
        params.Single(name='season', label=_('season'),
                      choices=[('spring', _('Spring')),
                               ('summer', _('Summer')),
                               ('autumn', _('Autumn')),
                               ('winter', _('Winter'))]),
    ]

    @classmethod
    def get_response(cls, request, content):
        return HttpResponse("PDF for %s" % content)
