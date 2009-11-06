from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import Base
from merengue.multimedia.models import Video


class VideoStreamming(Video):
    duration = models.FloatField(_('duration'), default=0)
    clip_id = models.CharField(_('clip id'), max_length=250)


class Channel(Base):
    pass


class Schedule(models.Model):
    broadcast_date = models.DateTimeField(verbose_name=_('broadcast date'))
    channel = models.ForeignKey(Channel, verbose_name=_('channel'))
    video = models.ForeignKey(VideoStreamming, verbose_name=_('video'))
