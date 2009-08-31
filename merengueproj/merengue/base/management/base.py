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


def copy_helper(style, name, directory):
    """
    Copies the merengue project tempalte into the specified directory.

    """
    # style -- A color style object (see django.core.management.color).
    # name -- The name of the project.
    # directory -- The directory to which the layout template should be copied.
    import re
    if not re.search(r'^[_a-zA-Z]\w*$', name): # If it's not a valid directory name.
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

    # Determine where the merengue project template is
    merengue_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
    skel_dir = os.path.abspath(os.path.join(merengue_root, 'projskel'))

    # Copy merengue project template
    copy_dir(skel_dir, top_dir, name, style)

    # Copy or symlink
    for d in 'apps', 'merengue', 'plugins':
        dest = os.path.join(top_dir, d)
        os.makedirs(dest)
        copy_dir(d, dest, name, style)


def copy_dir(source, dest, name, style, link=False):
    for d, subdirs, files in os.walk(source):
        relative_dir = d[len(source)+1:].replace('project_name', name)
        if relative_dir:
            os.mkdir(os.path.join(dest, relative_dir))
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
