from django.db.models import permalink
from django.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent, BaseCategory
from merengue.base.managers import BaseContentManager


class FeatureCategory(BaseCategory):

    class Meta:
        verbose_name = _('feature category')
        verbose_name_plural = _('features categories')


class Feature(BaseContent):

    categories = models.ManyToManyField(FeatureCategory,
                                        verbose_name=_('category'),
                                        blank=True, null=True, db_index=True)

    class Meta:
        verbose_name = _('feature')
        verbose_name_plural = _('features')
        content_view_template = 'features/features_view.html'

    @permalink
    def public_link(self):
        return ('features_view', [self.slug])

    objects = BaseContentManager()
