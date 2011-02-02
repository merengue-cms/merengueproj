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


from django.conf.urls.defaults import url
from django.conf import settings


def merengue_url(regex, view, kwargs=None, name=None, prefix=''):
    if isinstance(regex, dict):
        regex_translatable = regex.get(settings.LANGUAGE_CODE, None)
        if regex_translatable is None:
            regex_translatable = regex.get(getattr(settings,
                                            'URL_DEFAULT_LANG'), 'en')
    else:
        regex_translatable = regex
    return url(regex_translatable, view, kwargs, name, prefix)
