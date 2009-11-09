# -*- coding: utf-8 -*-
from merengue.base.admin import BaseAdmin
from merengue.multimedia.admin import BaseMultimediaAdmin, VideoAdmin
from plugins.tv.models import Channel, Schedule, VideoStreaming


class ChannelAdmin(BaseAdmin):
    pass


class ScheduleAdmin(BaseAdmin):
    pass


class VideoStreamingAdmin(VideoAdmin):

    exclude = ('authors', 'file', 'external_url')

    def get_form(self, request, obj=None):
        form = super(BaseMultimediaAdmin, self).get_form(request, obj)

        def clean(self):
            super(form, self).clean()
            return self.cleaned_data
        form.clean = clean
        return form


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
