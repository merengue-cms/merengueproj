from action.models import RegisteredAction
from registry import params
from registry.items import RegistrableItem
from django.utils.translation import ugettext_lazy as _


class BaseAction(RegistrableItem):
    model = RegisteredAction

    @classmethod
    def get_category(cls):
        return 'action'

    # do some stuff


class SiteAction(BaseAction):
    pass


class UserAction(BaseAction):
    pass


class ContentAction(BaseAction):
    pass


class PDFExport(ContentAction):
    # note: this config params are only for debugging purposes. remove it after was useful
    config_params = [
        params.Single(name='username', label=_('username'), default='pepe'),
        params.Single(name='bestfriend', label=_('bestfriend'), default='juan'),
        params.List(name='friends', label=_('friends'), default=['antonio', 'juan'],
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
