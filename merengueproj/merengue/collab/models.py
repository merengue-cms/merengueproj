# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from transmeta import TransMeta


REVISOR_RESULTS = (
    ('just', _('Just set status')),
    ('replace', _('Display an alternative comment in public view')),
    ('hide', _('Hide comment from public view')),
)


class CollabCommentType(models.Model):
    __metaclass__ = TransMeta

    name = models.CharField(
        _('name'),
        max_length=20,
        )

    label = models.CharField(
        _('label'),
        max_length=100,
        )

    class Meta:
        abstract = True
        translate = ('label', )

    def __unicode__(self):
        return self.label


class CollabCommentUserType(CollabCommentType):
    pass


class CollabCommentRevisorStatusType(CollabCommentType):

    decorator = models.ImageField(
        _('decorator'),
        upload_to='revisor_status_types',
        blank=True,
        null=True,
        )

    result = models.CharField(
        _('result'),
        max_length=30,
        choices=REVISOR_RESULTS,
        default="just",
        help_text=_('Select the resulting action this status trigger'),
        )

    reason = models.TextField(
        _('reason'),
        blank=True,
        null=True,
        )

    class Meta:
        translate = ('reason', )


class CollabComment(models.Model):
    # Generic Foreign Key
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('content type'),
        related_name="content_type_set_for_%(class)s",
        )
    object_pk = models.PositiveIntegerField(
        _('object ID'),
        )
    content_object = generic.GenericForeignKey(
        ct_field="content_type",
        fk_field="object_pk",
        )

    # User commenting (Authenticated)
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        blank=True,
        null=True,
        related_name="%(class)s_comments",
    )

    # User commenting (Non Authenticated)
    user_name = models.CharField(
        _("user's name"),
        max_length=50,
        blank=True,
        )
    user_email = models.EmailField(
        _("user's email address"),
        blank=True,
        )
    user_url = models.URLField(
        _("user's URL"),
        blank=True,
        )

    comment_user_type = models.ForeignKey(
        CollabCommentUserType,
        verbose_name=_('comment user type'),
        )

    comment = models.TextField(
        _('comment'),
        )

    submit_date = models.DateTimeField(
        _('date/time submitted'),
        default=None,
        auto_now_add=True,
        )
    ip_address = models.IPAddressField(
        _('IP address'),
        blank=True,
        null=True,
        )

    class Meta:
        ordering = ('submit_date', )
        permissions = [("can_revise", "Can revise comments")]
        verbose_name = _('collaborative comment')
        verbose_name_plural = _('collaborative comments')

    def get_user_name(self):
        return (self.user and (self.user.get_full_name() or self.user.username)) or self.user_name

    def get_user_email(self):
        if self.user:
            return self.user.email or ""
        else:
            return self.user_email

    def get_user_url(self):
        return self.user_url

    def get_last_revision_status(self):
        status_history = self.collabcommentrevisorstatus_set.order_by('-revision_date')
        if status_history.count():
            return status_history[0]
        else:
            return None


class CollabCommentRevisorStatus(models.Model):
    comment = models.ForeignKey(
        CollabComment,
        verbose_name=_('revised comment'),
    )

    # User that revises the comment
    revisor = models.ForeignKey(
        User,
        verbose_name=_('user'),
        blank=True,
        null=True,
        related_name="revised_%(class)s_comments",
    )

    type = models.ForeignKey(
        CollabCommentRevisorStatusType,
        verbose_name=_('revised comment status'),
        )

    revision_date = models.DateTimeField(
        _('date/time revised'),
        default=None,
        auto_now_add=True,
        )

    short_comment = models.CharField(
        _('short comment'),
        max_length=100,
        blank=True,
        null=True,
        )

    def __unicode__(self):
        return u'%s' % self.type
