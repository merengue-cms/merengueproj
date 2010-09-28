from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent
from merengue.base.managers import BaseContentManager


class Forum(BaseContent):

    objects = BaseContentManager()

    class Meta:
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')
        content_view_template = 'forum/forum_view.html'

    @permalink
    def public_link(self):
        return ('forum_view', [self.slug])

    def save(self, *args, **kwargs):
        self.commentable = 'disabled'
        super(Forum, self).save(*args, **kwargs)


class Thread(BaseContent):

    forum = models.ForeignKey(Forum)

    objects = BaseContentManager()

    class Meta:
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')
        content_view_template = 'forum/thread_view.html'

    @permalink
    def public_link(self):
        return ('thread_view', [self.forum.slug, self.slug])

    def save(self, *args, **kwargs):
        self.commentable = 'allowed'
        super(Thread, self).save(*args, **kwargs)
