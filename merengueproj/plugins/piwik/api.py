# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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

import urllib
import httplib
import urlparse

from django.utils import simplejson


class PiwikAPI:
    def __init__(self, url, token_auth):
        self.url = url
        self.token_auth = token_auth

        (scheme, netloc, path, query, fragment) = urlparse.urlsplit(self.url)
        self.host = netloc

    def call(self, method, params=None, format='json'):
        params = params or {}
        args = {'module': 'API',
                'method': method,
                'format': format,
                'token_auth': self.token_auth}

        args.update(params)
        conn = httplib.HTTPConnection(self.host)
        conn.request('GET', u"%s?%s" % (self.url, urllib.urlencode(args)),
                     headers={'User-Agent': 'Django Piwik'})
        result = conn.getresponse()
        data = None
        if result.status == 200:
            data = result.read()
        conn.close()
        if data is not None and format == 'json':
            return simplejson.loads(data)
        return data
