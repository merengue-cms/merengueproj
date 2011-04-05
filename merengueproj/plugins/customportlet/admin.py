from merengue.base.admin import BaseOrderableAdmin

from plugins.customportlet.forms import CustomPortletAdminModelForm
from plugins.customportlet.models import CustomPortlet


class CustomPortletAdmin(BaseOrderableAdmin):
    sortablefield = 'order'
    ordering = ('order', )
    html_fields = BaseOrderableAdmin.html_fields + ('description', )
    form = CustomPortletAdminModelForm


def register(site):
    """ Merengue admin registration callback """
    site.register(CustomPortlet, CustomPortletAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(CustomPortlet)
