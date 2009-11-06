from django import template


register = template.Library()


@register.inclusion_tag('tv/inc.video_player_js.html', takes_context=True)
def videoplayerjs(video):
    """Loads the required media an libraries for the video player. This
    should be used in the template <head>."""
    return {'channel': video.channel,
            'clipid': video.clipid}


@register.inclusion_tag('tv/inc.video_player.html', takes_context=True)
def videoplayer(video):
    """Embeds a video player. This should be used in the template <body>."""
    return {'channel': video.channel,
            'clipid': video.clipid}
