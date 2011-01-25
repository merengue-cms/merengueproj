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

from django.conf import settings
from django.template import Library

from merengue.theming.models import Theme

register = Library()


@register.filter
def replace_variables(value, arg=None):
    value = value.replace('$media_url', settings.MEDIA_URL)
    try:
        active_theme = Theme.objects.active()
        value = value.replace('$theme_url', active_theme.get_theme_media_url())
    except Theme.DoesNotExist:
        pass
    return value


@register.filter
def menu_less(value, min_level=None):
    if min_level:
        return value - min_level + 1
    return value
