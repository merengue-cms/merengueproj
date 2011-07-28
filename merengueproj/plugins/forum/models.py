import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent, BaseCategory
from merengue.base.managers import BaseContentManager


class ForumCategory(BaseCategory):

    class Meta:
        verbose_name = _('Forum category')
        verbose_name_plural = _('Forum categories')


class Forum(BaseContent):

    category = models.ForeignKey(ForumCategory,
                                 verbose_name=_('Category'))

    objects = BaseContentManager()

    class Meta:
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')
        content_view_function = 'plugins.forum.views.content_forum_view'
        content_view_template = 'forum/forum_view.html'
        check_slug_uniqueness = True

    def _public_link_without_section(self):
        return ('forum_view', [self.slug])

    def save(self, *args, **kwargs):
        self.commentable = 'disabled'
        super(Forum, self).save(*args, **kwargs)

    def get_all_comments(self):
        comments = ForumThreadComment.objects.filter(thread__in=[i['id'] for i in self.thread_set.all().values('id')]).order_by('-date_submitted')
        return comments

    def breadcrumbs_last_item(self):
        return (unicode(self), self.public_link_without_section())

    def get_last_comment(self):
        comments = self.get_all_comments()
        return comments and comments[0] or None


class Thread(BaseContent):

    forum = models.ForeignKey(Forum)
    closed = models.BooleanField(_('closed'), default=False)
    user = models.ForeignKey(User, editable=False)

    objects = BaseContentManager()

    class Meta:
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')
        content_view_template = 'forum/thread_view.html'

    def get_main_section(self):
        return self.forum.get_main_section()

    def _public_link_without_section(self):
        return ('thread_view', [self.forum.slug, self.slug])

    def save(self, *args, **kwargs):
        self.commentable = 'disabled'
        super(Thread, self).save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        super(Thread, self).validate_unique(exclude)
        if self.forum_id and self.forum.thread_set.filter(slug=self.slug).exclude(pk=self.pk).exists():
            raise ValidationError({'slug': (ugettext('The slug already exists in other thread in this forum'),)})

    def get_last_comment(self):
        comments = ForumThreadComment.objects.filter(thread=self).order_by('-date_submitted')
        return comments and comments[0] or None

    @permalink
    def get_admin_absolute_url(self):
        parent_content_type = ContentType.objects.get_for_model(self.forum)
        return ('merengue.base.views.admin_link', [parent_content_type.id, self.forum.id, 'thread/%s/' % self.id])

    def breadcrumbs_first_item(self):
        return []

    def breadcrumbs_items(self):
        thread_breadcrumbs = super(Thread, self).breadcrumbs_items()
        forum_breadcrumbs = self.forum.breadcrumbs_items()
        forum_breadcrumbs.extend(thread_breadcrumbs)
        return forum_breadcrumbs


class ForumThreadComment(models.Model):

    thread = models.ForeignKey(Thread)
    parent = models.ForeignKey('self', null=True, blank=True, default=None, related_name='children')
    user = models.ForeignKey(User)

    # Content Fields
    title = models.CharField(_('title'), max_length=255)
    comment = models.TextField(_('comment'))

    # Meta Fields
    banned = models.BooleanField(_('banned'), default=False)
    date_submitted = models.DateTimeField(_('date/time submitted'), default=datetime.datetime.now)
    date_modified = models.DateTimeField(_('date/time modified'), default=datetime.datetime.now)
    ip_address = models.CharField(_('IP address'), max_length=150, null=True, blank=True)

    class Meta:
        ordering = ('-date_submitted', )
        verbose_name = _("Forum Thread Comment")
        verbose_name_plural = _("Forum Thread Comments")
        get_latest_by = "date_submitted"

    def is_public(self):
        return not self.banned

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self)
        return ('merengue.base.views.admin_link', [content_type.id, self.id, ''])
