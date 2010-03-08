from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import ContentAction
from merengue.registry import params


class HomeInitialContent(ContentAction):
    name = 'home_initial_content'
    verbose_name = _('Home initial content')

    config_params = [
        params.Single(name='home_initial_content',
                      label=_('home initial content'), default='1')
    ]

    @classmethod
    def get_response(cls, request, content):
        return HttpResponse("home initial content %s" % content)
