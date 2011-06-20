from django.utils.translation import ugettext_lazy as _
from merengue.base.forms import BaseAdminModelForm
from merengue.perms.models import Role


class PortalLinkForm(BaseAdminModelForm):

    def __init__(self, *args, **kwargs):
        super(PortalLinkForm, self).__init__(*args, **kwargs)
        self.fields['visible_by_roles'].queryset = Role.objects.without_anonymoususer()

    def clean(self):
        cleaned_data = super(PortalLinkForm, self).clean()
        if cleaned_data.get('content') and cleaned_data.get('external_url'):
            content_url_error = _('Link cannot point to an url if already points to content')
            self._errors["external_url"] = self.error_class([content_url_error])
            del cleaned_data["external_url"]
        return cleaned_data
