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

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from merengue.multimedia.models import Video, Audio


def video_xml(request, video_id, height=None, width=None):
    """ Prepare xml for flvplayer """

    videoitem = get_object_or_404(Video, id=video_id)
    video_info = dict(video=videoitem.video)
    height = request.GET.get('height', height)
    width = request.GET.get('width', width)
    if height:
        video_info['height'] = height

    if width:
        video_info['width'] = width

    if videoitem.video.preview:
        video_info['preview'] = videoitem.video.preview

    return render_to_response('multimedia/video.xml',
                              {'video_info': video_info},
                              context_instance=RequestContext(request),
                              mimetype="application/xml")


def audio_xml(request, audio_id, height=None, width=None):
    """ Prepare xml for flvplayer """

    audioitem = get_object_or_404(Audio, id=audio_id)

    return render_to_response('multimedia/audio.xml',
                              {'audio': audioitem.audio},
                              context_instance=RequestContext(request),
                              mimetype="application/xml")
