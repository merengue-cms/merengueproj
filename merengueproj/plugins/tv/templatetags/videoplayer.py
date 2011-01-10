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

from django import template


register = template.Library()


@register.inclusion_tag('tv/inc.video_player_js.html')
def videoplayerjs(video):
    """Loads the required media an libraries for the video player. This
    should be used in the template <head>."""
    return {'channel': video.channel,
            'clipid': video.clip_id}


@register.inclusion_tag('tv/inc.video_player.html')
def videoplayer(video):
    """Embeds a video player. This should be used in the template <body>."""
    return {'channel': video.channel,
            'clipid': video.clip_id}
