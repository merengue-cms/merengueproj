from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from merengue.multimedia.models import Video


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
