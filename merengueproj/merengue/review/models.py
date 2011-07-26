# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from merengue.review.utils import send_mail_content_as_pending, get_reviewers


class ReviewTask(models.Model):
    owner = models.ForeignKey(User, verbose_name=_(u'owner'), related_name='owned_by')
    assigned_to = models.ManyToManyField(User, verbose_name=_(u'assigned to'), related_name='assigned_to')
    title = models.CharField(verbose_name=_(u'title'), max_length=1024)
    description = models.TextField(verbose_name=_(u'description'), blank=True)
    url = models.CharField(verbose_name=_(u'url'), max_length=1024, blank=True, null=True)
    is_done = models.BooleanField(verbose_name=_(u'is done'), default=False)

    task_object_type = models.ForeignKey(ContentType, verbose_name=_(u'object type'),
                                        blank=True, null=True, related_name="review_tasks")
    task_object_id = models.PositiveIntegerField(verbose_name=_(u'object id'),
                                        blank=True, null=True, db_index=True)
    task_object = generic.GenericForeignKey('task_object_type', 'task_object_id')

    class Meta:
        ordering = ('is_done', 'title', 'url', 'owner', )

    def __unicode__(self):
        if self.is_done:
            done = _('done')
        else:
            done = _('not done')
        return "%s (%s)" % (self.title, done)


def notify_review_task(sender, instance, created, **kwargs):
    if created and getattr(settings, 'SEND_MAIL_IF_PENDING', False):
        if not ReviewTask.objects.filter(
            is_done=False, task_object_id=instance.task_object_id).count() > 1:
            # disclaimer: the assigned users are not selected using instance
            # because they're not updated, because M2M fields are updated
            # after the post_save signal
            assigned = get_reviewers(instance.task_object)
            send_mail_content_as_pending(instance.task_object, instance,
                                         [instance.owner] + assigned)


post_save.connect(notify_review_task, sender=ReviewTask)
