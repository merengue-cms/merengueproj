from django.shortcuts import get_object_or_404

from merengue.base.views import content_view

from plugins.event.models import VideoStreaming


def video_index(request):
#    video_list = _get_event_search_context(EventQuickSearchForm)
#    return object_list(request, video_list)
    pass


def video_view(request, video_id):
    video = get_object_or_404(VideoStreaming, id=video_id)

    return content_view(request, video, 'tv/video_view.html')
