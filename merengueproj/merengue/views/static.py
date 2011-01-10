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

import mimetypes
import os
import posixpath
import stat
import urllib

from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         HttpResponseNotModified)
from django.utils.http import http_date
from django.utils.functional import memoize
from django.views.static import directory_index, was_modified_since

from merengue.pluggable.models import RegisteredPlugin


_plugins_full_path_cache = {}


def get_plugins_full_path():
    all_plugins = RegisteredPlugin.objects.all().order_by('-active')
    paths = dict([(p.directory_name, p.get_path()) for p in all_plugins])
    return paths
get_plugins_full_path = memoize(get_plugins_full_path, _plugins_full_path_cache, 1)


def serve(request, path, document_root=None, show_indexes=False):
    """
    Serve static files combining media dirs for all plugins and apps.

    This is based on django.views.static.serve.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'merengue.views.static.serve', {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """

    # Clean up given path to only allow serving files below document_root.
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    plugin = None
    plugins_paths = get_plugins_full_path()
    plugins_names = plugins_paths.keys()
    newpath = ''
    fallback_newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        if not newpath and not plugin and part in plugins_names:
            # Plugins media dir must come first in the URL
            plugin = part
            fallback_newpath = os.path.join(newpath, part).replace('\\', '/')
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    fallback_newpath = os.path.join(fallback_newpath, newpath).replace('\\', '/')
    if not plugin and newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    # project media dir, standard django's static serve behavior
    if plugin:
        fullpath = os.path.join(plugins_paths[plugin], 'media', newpath)
        try:
            return _serve_path(request, newpath, fullpath, show_indexes)
        except Http404:
            fullpath = os.path.join(document_root, fallback_newpath)
            return _serve_path(request, fallback_newpath, fullpath, show_indexes)
    else:
        fullpath = os.path.join(document_root, newpath)
        return _serve_path(request, newpath, fullpath, show_indexes)


def _serve_path(request, newpath, fullpath, show_indexes):
    if os.path.isdir(fullpath):
        if show_indexes:
            return directory_index(newpath, fullpath)
        raise Http404("Directory indexes are not allowed here.")
    if not os.path.exists(fullpath):
        raise Http404('"%s" does not exist' % fullpath)
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified()
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    response["Content-Length"] = len(contents)
    return response
