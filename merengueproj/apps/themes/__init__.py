import os

from django.conf import settings
from django.utils._os import safe_join


def get_theme_root_dirs(template_dirs=None):
    """ Returns all themes root directories found """
    if not template_dirs:
        template_dirs = settings.TEMPLATE_DIRS
    for template_dir in template_dirs:
        yield safe_join(template_dir, 'themes')


def get_theme_dirs(template_dirs=None):
    """ Returns all theme directories"""
    for themes_root in get_theme_root_dirs():
        for theme_dir in os.listdir(themes_root):
            yield theme_dir, safe_join(themes_root, theme_dir)
