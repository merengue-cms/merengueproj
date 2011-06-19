from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import SiteAction


class FooAction(SiteAction):
    name = 'fooaction'
    verbose_name = _('Foo action')
    help_text = _('Foo action')

    def get_response(self, request):
        return HttpResponseRedirect(reverse('foomodel_index'))
