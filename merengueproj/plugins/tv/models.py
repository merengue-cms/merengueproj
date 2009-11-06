from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import Base
from merengue.multimedia.models import Video


class VideoStreaming(Video):
    duration = models.FloatField(_('duration'), default=0)
    clip_id = models.CharField(_('clip id'), max_length=250)
    channel = models.CharField(_('channel'), max_length=250,
                               help_text='Channel in Livestream')


class Channel(Base):
    pass


class Schedule(models.Model):
    broadcast_date = models.DateTimeField(('broadcast date'))
    channel = models.ForeignKey(Channel, verbose_name=_('channel'),
                                related_name='schedules')
    video = models.ForeignKey(VideoStreaming, verbose_name=_('video'),
                              related_name='schedules')
