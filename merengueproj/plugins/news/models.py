from django.db import models
from django.utils.translation import ugettext_lazy as _

from transmeta import TransMeta

from base.models import BaseContent, BaseCategory
from plugins.news.managers import NewsItemManager


class Cosa(models.Model):
    nol = models.AutoField(primary_key=True)


class NewsCategory(BaseCategory):

    class Meta:
        verbose_name = _('news category')
        verbose_name_plural = _('news categories')


class NewsItem(BaseContent):
    __metaclass__ = TransMeta

    publish_date = models.DateTimeField(blank=True, null=True, db_index=True)
    expire_date = models.DateTimeField(blank=True, null=True, db_index=True)
    categories = models.ManyToManyField(NewsCategory,
                                        verbose_name=_('category'),
                                        blank=True, null=True, db_index=True)
    body = models.TextField(_('body'))

    objects = NewsItemManager()

    class Meta:
        translate = ('body', )
