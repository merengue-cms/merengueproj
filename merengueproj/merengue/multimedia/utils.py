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

from threading import local

from merengue.multimedia.datastructures import MediaDictionary

_content_holder = local()


def get_content_holder():
    """
    Returns media bundled contents
    """
    return _content_holder.data


def activate_media():
    """
    Initialize media contents for render_bundled_media and addmedia tags
    """
    _content_holder.data = MediaDictionary()


def deactivate_media():
    """
    Uninitialize media contents for render_bundled_media and addmedia tags
    """
    if hasattr(_content_holder, "data"):
        del _content_holder.data
