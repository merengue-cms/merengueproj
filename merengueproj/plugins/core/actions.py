from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import UserAction


class LoginAction(UserAction):
    name = 'login'
    verbose_name = _('Login')

    @classmethod
    def get_url(cls, request, user):
        login_url = reverse('merengue_login')
        if request.get_full_path() != reverse('merengue_logout'): # to avoid automatic logout after login
            login_url += '?next=%s' % request.get_full_path()
        return login_url

    @classmethod
    def has_action(cls, user):
        return not user.is_authenticated()


class LogoutAction(UserAction):
    name = 'logout'
    verbose_name = _('Logout')

    @classmethod
    def get_url(cls, request, user):
        return reverse('merengue_logout')

    @classmethod
    def has_action(cls, user):
        return user.is_authenticated()
