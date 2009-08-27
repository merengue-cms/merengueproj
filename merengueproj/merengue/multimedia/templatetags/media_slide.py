from django import template


register = template.Library()


@register.inclusion_tag('media_slide.html', takes_context=True)
def media_slide(context, content):
    content_images = content.multimedia.photos().published().order_by('multimediarelation__order')
    content_videos = content.multimedia.videos().published().order_by('multimediarelation__order')
    content_image3d = content.multimedia.images3d().published().order_by('multimediarelation__order')
    content_panoramicview = content.multimedia.panoramic_views().published().order_by('multimediarelation__order')
    return {'content': content,
            'content_images': content_images,
            'content_videos': content_videos,
            'content_image3d': content_image3d,
            'content_panoramicview': content_panoramicview,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }
