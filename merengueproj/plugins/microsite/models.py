from django.utils.translation import ugettext_lazy as _
from merengue.section.models import Section


class MicroSite(Section):

    class Meta:
        verbose_name = _('microsite')
        verbose_name_plural = _('microsites')
