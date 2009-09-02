from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import ContentAction


class FacebookLink(ContentAction):
    name = 'facebooklink'
    verbose_name = _('Link at Facebook')

    @classmethod
    def get_response(cls, request, content):
        request_url = 'http://%s%s' % (request.get_host(), content.public_link())
        return HttpResponseRedirect('http://www.facebook.com/share.php?u=%s' % urlquote(request_url))
