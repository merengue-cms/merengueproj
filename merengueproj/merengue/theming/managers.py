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

from django.db import models

_cached_active_theme = None


class ThemeManager(models.Manager):
    """ Theme manager """

    def active(self):
        """ Retrieves active theme for site """
        global _cached_active_theme
        if _cached_active_theme is None:
            _cached_active_theme = self.get(active=True)
        return _cached_active_theme

    def clear_cache(self):
        global _cached_active_theme
        _cached_active_theme = None
