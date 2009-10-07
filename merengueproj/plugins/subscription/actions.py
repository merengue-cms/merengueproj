from django.core.urlresolvers import reverse

from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import ContentAction


class SubscriptionAction(ContentAction):
    name = 'subscriptionaction'
    verbose_name = _('Subscription')

    @classmethod
    def get_response(cls, request, content):
        return HttpResponseRedirect(reverse("subscription_form", args=(content.slug, )))

    @classmethod
    def has_action(cls, content):
        return content.subscribable_set.actives()
