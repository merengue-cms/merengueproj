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

from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent
from merengue.multimedia.models import Video


class VideoStreaming(Video):
    duration = models.FloatField(_('duration'), default=0)
    clip_id = models.CharField(_('clip id'), max_length=250)
    channel = models.CharField(_('channel'), max_length=250,
                               help_text='Channel in Livestream')


class Channel(BaseContent):

    @permalink
    def public_link(self):
        return ('channel_view', (self.slug, ))


class Schedule(models.Model):
    broadcast_date = models.DateTimeField(('broadcast date'),
                                          help_text=_('In hours'))
    channel = models.ForeignKey(Channel, verbose_name=_('channel'),
                                related_name='schedules',
                               )
    video = models.ForeignKey(VideoStreaming, verbose_name=_('video'),
                              related_name='schedules')
