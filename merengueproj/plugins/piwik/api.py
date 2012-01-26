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

from merengue.pluggable.utils import get_plugin
from plugins.piwik.settings import PERIOD, DATE, METRIC


class PiwikAPI(object):

    def __init__(self, url=None, token_auth=None):
        self.config = get_plugin('piwik').get_config()
        self.url = url or self.get_piwik_url()
        self.token_auth = token_auth or self.get_token()
        (scheme, netloc, path, query, fragment) = urlparse.urlsplit(self.url)
        self.host = netloc

    def get_period(self):
        return self.config.get('period').get_value() or PERIOD

    def get_date(self):
        return self.config.get('date').get_value() or DATE

    def get_metric(self):
        return self.config.get('metric').get_value() or METRIC

    def get_site_id(self):
        return self.config.get('site_id').get_value()

    def get_piwik_url(self):
        return self.config.get('url').get_value()

    def get_token(self):
        return self.config.get('token').get_value()

    def call(self, method, params=None, format='json'):
        params = params or {}
        args = {'module': 'API',
                'method': method,
                'format': format,
                'token_auth': self.token_auth,
                'idSite': self.get_site_id(),
                'period': self.get_period(),
                'date': self.get_date()}
        args.update(params)
        conn = httplib.HTTPConnection(self.host)
        conn.request('GET', u"%s?%s" % (self.url, urllib.urlencode(args)),
                     headers={'User-Agent': 'Django Piwik'})
        result = conn.getresponse()
        data = None
        if result.status == 200:
            data = result.read()
        else:
            data = '{"result":"error", "message":"%s"}' % (httplib.responses.get(result.status, None) or 'Unknow')
        conn.close()
        if data is not None and format == 'json':
            return simplejson.loads(data)
        return data
