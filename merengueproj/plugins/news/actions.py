from django.utils.translation import ugettext_lazy as _

from action.actions import ContentAction
from registry import params


class PDFExport(ContentAction):
    # note: this config params are only for debugging purposes. remove it
    # after was useful
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
