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
Base classes for writing Merengue management commands (to be executed
through ``merengue-admin.py``).

"""
import os
import shutil
import sys

from django.core.management.base import (BaseCommand, CommandError,
                                         _make_writeable)


class MerengueCommand(BaseCommand):
    """
    Base class for all the commands in Merengue.

    Commands extending this class will be accesible through merengue-admin.py
    and the manage.py of merengue projects.

    All details for Django management commands apply.

    """

    pass


def copy_helper(style, name, directory, symlink=False):
    """
    Copies the merengue project template into the specified directory.

    If symlink is True then Merengue and its directories (apps and plugins)
    will be symlinked instead of copied. This is useful for developers of
    the Merengue core.

    """
    # style -- A color style object (see django.core.management.color).
    # name -- The name of the project.
    # directory -- The directory to which the layout template should be copied.
    import re
    from merengue import settings as merengue_settings
    if not re.search(r'^[_a-zA-Z]\w*$', name):  # If it's not a valid directory name.
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', name):
            message = 'make sure the name begins with a letter or underscore'
        else:
            message = 'use only numbers, letters and underscores'
        raise CommandError("%r is not a valid project name. Please %s." % (name, message))
    top_dir = os.path.join(directory, name)
    try:
        os.mkdir(top_dir)
    except OSError, e:
        raise CommandError(e)

    merengue_root = merengue_settings.MERENGUEDIR

    skel_dir = os.path.join(merengue_root, 'skel', 'project')

    # Copy merengue project template
    copy_dir(skel_dir, top_dir, name, False, style)

    # Copy or symlink all needed subdirectories
    copy_merengue_dirs(style, name, merengue_root, top_dir, symlink)


def copy_merengue_dirs(style, name, merengue_root, top_dir, symlink, remove_if_exists=False):
    """ Copy or symlink all needed merengue directories """

    merengue_parent_dir = os.path.split(merengue_root)[0]

    if sys.platform == 'win32':
        message = "Linking is not supported by this platform (%s), copying instead." % sys.platform
        sys.stderr.write(style.NOTICE(message))
        symlink = False
        symlink_possible = False
    else:
        symlink_possible = True

    # Symlink "merengue" top dir
    if symlink:
        dest = os.path.join(top_dir, 'merengue')
        make_symlink(merengue_root, dest, remove_if_exists)
    else:
        dest = os.path.join(top_dir, 'merengue')
        copy_dir(merengue_root, dest, name, remove_if_exists, style)

    # Copy or symlink merengue plugins
    dest = os.path.join(top_dir, 'plugins')
    if symlink:
        make_symlink(os.path.join(merengue_parent_dir, 'plugins'), dest, remove_if_exists)
    else:
        os.makedirs(dest)
        copy_dir(os.path.join(merengue_parent_dir, 'plugins'), dest, name, remove_if_exists, style)

    # Symlink merengue's media
    merengue_media_dir = os.path.join(top_dir, 'media', 'merengue')
    if not symlink_possible:
        message = "Linking is not supported by this platform (%s), copying merengue/media instead."
        sys.stderr.write(style.NOTICE(message % sys.platform))
        copy_dir(os.path.join(merengue_root, 'media'), merengue_media_dir, name, remove_if_exists, style)
    else:
        make_symlink(os.path.join('..', 'merengue', 'media'), merengue_media_dir, remove_if_exists)

    # Copy or symlink default themes' media and templates
    themes_dir = os.path.join(merengue_root, 'themes')
    for theme in os.listdir(themes_dir):
        if theme.startswith('.'):
            continue  # we ignore hidden directories
        theme_dir = os.path.join(themes_dir, theme)
        dest_media = os.path.join(top_dir, 'media', 'themes', theme)
        dest_templates = os.path.join(top_dir, 'templates', 'themes', theme)
        if symlink:
            make_symlink(os.path.join('..', '..', 'merengue', 'themes', theme, 'media'), dest_media, remove_if_exists)
            make_symlink(os.path.join('..', '..', 'merengue', 'themes', theme, 'templates'), dest_templates, remove_if_exists)
        else:
            copy_dir(os.path.join(theme_dir, 'media'), dest_media, name, remove_if_exists, style)
            copy_dir(os.path.join(theme_dir, 'templates'), dest_templates, name, remove_if_exists, style)


def make_symlink(link_src, link_dst, remove_if_exists):
    if remove_if_exists:
        remove_dst_if_exist(link_dst)
    os.symlink(link_src, link_dst)


def remove_dst_if_exist(dst):
    if os.path.exists(dst):
        if os.path.islink(dst) or os.path.isfile(dst):
            os.remove(dst)
        else:
            shutil.rmtree(dst)


def copy_dir(source, dest, name, remove_if_exists, style, link=False):
    """ Copy directory recursively from a template directory """
    if remove_if_exists:
        remove_dst_if_exist(dest)
        os.makedirs(dest)

    for d, subdirs, files in os.walk(source):
        relative_dir = d[len(source) + 1:].replace('project_name', name)
        new_relative_dir = os.path.join(dest, relative_dir)
        if not os.path.exists(new_relative_dir):
            os.makedirs(new_relative_dir)
        for i, subdir in enumerate(subdirs):
            if subdir.startswith('.'):
                del subdirs[i]
        for f in files:
            if f.endswith('.pyc'):
                continue
            path_old = os.path.join(d, f)
            path_new = os.path.join(dest, relative_dir, f.replace('project_name', name))
            fp_old = open(path_old, 'r')
            fp_new = open(path_new, 'w')
            fp_new.write(fp_old.read().replace('{{ project_name }}', name))
            fp_old.close()
            fp_new.close()
            try:
                shutil.copymode(path_old, path_new)
                _make_writeable(path_new)
            except OSError:
                sys.stderr.write(style.NOTICE("Notice: Couldn't set permission bits on %s. You're probably using an uncommon filesystem setup. No problem.\n" % path_new))
