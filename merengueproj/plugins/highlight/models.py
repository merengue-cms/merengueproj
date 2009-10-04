from django.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import Base, BaseContent


class Highlight(Base):
    weight = models.IntegerField(_('weight to decide ordering'), default=0)
    related_content = models.ForeignKey(BaseContent, verbose_name=_('related content'),
                                        null=True, blank=True)

    class Meta:
        ordering = ('-weight', )

    def get_absolute_url(self):
        if self.related_content:
            return self.related_content.get_absolute_url()
        else:
            return '#'
