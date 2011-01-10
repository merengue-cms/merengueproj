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

from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

# place app url patterns here
urlpatterns = patterns('merengue.multimedia.views',
#    url(r'^videos/(?P<video_id>[\w-]+)/(?P<width>\d+)x(?P<height>\d+)/video.xml$', 'video_xml', name='video_xml'),
    url(r'^videos/(?P<video_id>[\w-]+)/video.xml$', 'video_xml', name='video_xml'),
    url(r'^audios/(?P<audio_id>[\w-]+)/audio.xml$', 'audio_xml', name='audio_xml'),
)
