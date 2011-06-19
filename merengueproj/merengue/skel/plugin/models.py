from django.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent
from merengue.base.managers import BaseContentManager


class FooModel(BaseContent):
    """ A test model in plugin skel """

    extra_field = models.CharField(verbose_name=_('extra field'),
                                   max_length=100, blank=True, null=True)

    objects = BaseContentManager()

    class Meta:
        translate = ('extra_field', )
        content_view_template = 'foomodel_view.html'
        verbose_name = _('foomodel')
        verbose_name_plural = _('foomodels')
