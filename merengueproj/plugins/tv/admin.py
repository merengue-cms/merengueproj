# -*- coding: utf-8 -*-
from merengue.base.admin import BaseAdmin
from merengue.multimedia.admin import VideoAdmin
from plugins.tv.models import Channel, Schedule, VideoStreaming


class ChannelAdmin(BaseAdmin):
    pass


class ScheduleAdmin(BaseAdmin):
    pass


class VideoStreamingAdmin(VideoAdmin):
    pass


def register(site):
    """ Merengue admin registration callback """
    site.register(Channel, ChannelAdmin)
    site.register(Schedule, ScheduleAdmin)
    site.register(VideoStreaming, VideoStreamingAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Channel)
    site.unregister(Schedule)
    site.unregister(VideoStreaming)
