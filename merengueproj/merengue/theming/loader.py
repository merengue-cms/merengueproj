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
