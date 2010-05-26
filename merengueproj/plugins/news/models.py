import datetime

from django.db import models
from django.db.models import permalink
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _

from cmsutils.cache import CachingManager

from merengue.base.models import BaseContent, BaseCategory
from plugins.news.managers import NewsItemManager


class NewsCategory(BaseCategory):

    class Meta:
        verbose_name = _('news category')
        verbose_name_plural = _('news categories')

    objects = CachingManager(cache_object_retrieval=True)


class NewsItem(BaseContent):

    publish_date = models.DateTimeField(blank=True, null=True, db_index=True)
    expire_date = models.DateTimeField(blank=True, null=True, db_index=True)
    categories = models.ManyToManyField(NewsCategory,
                                        verbose_name=_('category'),
                                        blank=True, null=True, db_index=True)
    body = models.TextField(_('body'))

    objects = NewsItemManager()

    class Meta:
        translate = ('body', )
        content_view_template = 'news/newsitem_view.html'
        ordering = ('-publish_date', '-id')

    @permalink
    def public_link(self):
        section = self.get_main_section()
        if section is None:
            return ('newsitem_view', [self.slug])
        else:
            # go to news item inside section which created it
            return ('content_section_view', [section.slug, self.id, self.slug])


def set_publish_date(sender, instance, **kwargs):
    if instance.status == 'published' and not instance.publish_date:
        instance.publish_date = datetime.datetime.now()

pre_save.connect(set_publish_date, sender=NewsItem)
