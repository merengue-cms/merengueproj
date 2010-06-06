import os
from os import path

from django.conf import settings
from django.utils._os import safe_join


def get_theme_root_dirs(template_dirs=None):
    """ Returns all themes root directories found """
    if not template_dirs:
        template_dirs = settings.TEMPLATE_DIRS
    for template_dir in template_dirs:
        template_path = safe_join(template_dir, 'themes')
        if os.path.isdir(template_path):
            yield template_path


def get_theme_dirs(template_dirs=None):
    """ Returns all theme directories"""
    for themes_root in get_theme_root_dirs():
        for theme_dir in os.listdir(themes_root):
            if path.isdir(safe_join(themes_root, theme_dir)) and \
               not theme_dir.startswith('.'):
                yield theme_dir, safe_join(themes_root, theme_dir)


def get_theme_path(directory_name=None):
    for theme_dir, theme_path in get_theme_dirs():
        if directory_name == theme_dir:
            return theme_path
