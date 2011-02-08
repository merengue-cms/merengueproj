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

from merengue.multimedia.datastructures import MediaDictionary


class MediaMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and initializes the media bundle object in the current
    thread context.
    """

    def process_request(self, request):
        """ Initialize media contents for render_bundled_media and addmedia tags """
        request.media_holder = MediaDictionary()

    def process_response(self, request, response):
        """ Uninitialize media contents for render_bundled_media and addmedia tags """
        if hasattr(request, 'media_holder'):
            del request.media_holder
        return response
