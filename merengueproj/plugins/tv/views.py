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

from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

from merengue.base.views import content_view

from plugins.tv.models import Channel, VideoStreaming


def tv_index(request):
    channels = Channel.objects.all()
    return render_to_response('tv/tv_index.html', {'channels': channels},
                              context_instance=RequestContext(request))


def channel_view(request, channel_slug):
    channel = get_object_or_404(Channel, slug=channel_slug)
    now = datetime.now()
    videos = [schedule.video for schedule in channel.schedules.filter(broadcast_date__lte=now)
                             if now < schedule.broadcast_date + timedelta(seconds=3600*schedule.video.duration)]
    video = videos and videos[0] or channel.schedules.all() and channel.schedules.all()[0].video or None
    return content_view(request, channel, 'tv/channel_view.html', {'video': video,
                                                                    'channel': channel})


def video_view(request, video_id):
    video = get_object_or_404(VideoStreaming, id=video_id)
    return content_view(request, video, 'tv/video_view.html')
