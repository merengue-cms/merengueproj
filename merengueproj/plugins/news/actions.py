from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import ContentAction
from merengue.registry import params


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
    def get_response(cls, request):
        return HttpResponse("PDF from %s" % request.get_full_path())
