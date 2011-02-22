from django.utils.translation import ugettext_lazy as _
from merengue.base.forms import BaseAdminModelForm


class PortalLinkForm(BaseAdminModelForm):

    def clean(self):
        cleaned_data = super(PortalLinkForm, self).clean()
        if cleaned_data.get('content') and cleaned_data.get('external_url'):
            content_url_error = _('Link cannot point to an url if already points to content')
            self._errors["external_url"] = self.error_class([content_url_error])
            del cleaned_data["external_url"]
        return cleaned_data
