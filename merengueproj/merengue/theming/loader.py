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

"""
Loading templates from active theme looking for directories in TEMPLATE_DIRS/themes
"""
import os

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.utils._os import safe_join

from merengue.theming import get_theme_root_dirs


def get_template_sources(template_name, template_dirs=None):
    """
    Look for template into active theme directory
    """
    from merengue.theming.models import Theme
    try:
        active_theme = Theme.objects.active()
    except Theme.DoesNotExist:
        return
    for themes_dir in get_theme_root_dirs(template_dirs):
        active_theme_dir = safe_join(themes_dir, active_theme.directory_name)
        if os.path.isdir(active_theme_dir):
            try:
                yield safe_join(active_theme_dir, template_name)
            except UnicodeDecodeError:
                raise
            except ValueError:
                pass


def load_template_source(template_name, template_dirs=None):
    tried = []
    for filepath in get_template_sources(template_name, template_dirs):
        try:
            return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
        except IOError:
            tried.append(filepath)
    if tried:
        error_msg = "Tried %s" % tried
    else:
        error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
    raise TemplateDoesNotExist(error_msg)
load_template_source.is_usable = True
load_template_source.is_usable = True
