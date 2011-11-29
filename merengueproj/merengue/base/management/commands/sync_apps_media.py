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

import os
import sys
import glob
import shutil
from optparse import make_option

from django.conf import settings
from django.utils.text import get_text_list
from django.core.management.base import CommandError, AppCommand
from django.utils.importlib import import_module

from merengue.base.management.base import MerengueCommand

try:
    set
except NameError:
    from sets import Set as set  # Python 2.3 fallback


class Command(AppCommand, MerengueCommand):
    """Copy or symlink media files from all INSTALLED_APPS applications to the
    MEDIA_ROOT of the project.

    Based on the build_media management command from Pinax:
    http://github.com/pinax/pinax/blob/0f12c3a3a4ac396eeba734a52a285c7e2d7a7ea7/pinax/apps/staticfiles/management/commands/build_media.py
    which in turn is based on the collectmedia management command by Brian Beck:
    http://blog.brianbeck.com/post/50940622/collectmedia
    """
    media_files = {}
    media_root = settings.MEDIA_ROOT
    exclude = ['CVS', '.*', '*~']
    option_list = AppCommand.option_list + (
        make_option('-i', '--interactive', action='store_true', dest='interactive',
            help="Run in interactive mode, asking before modifying files and selecting from multiple sources."),
        make_option('-e', '--exclude', action='append', default=exclude, dest='exclude', metavar='PATTERNS',
            help="A space-delimited list of glob-style patterns to ignore. Use multiple times to add more."),
        make_option('-n', '--dry-run', action='store_true', dest='dry_run',
            help="Do everything except modify the filesystem."),
        make_option('-l', '--link', action='store_true', dest='link',
            help="Create a symbolic link to each file instead of copying."),
    )
    help = 'Collect media files of apps in a single media directory.'
    args = '[appname appname ...]'

    def handle(self, *app_labels, **options):
        media_root = os.path.normpath(self.media_root)

        if not os.path.isdir(media_root):
            raise CommandError(
                'Designated media location %s could not be found.' % media_root)

        if options.get('dry_run', False):
            print "\n    DRY RUN! NO FILES WILL BE MODIFIED."
        print "\nCollecting media in %s" % media_root

        if app_labels:
            apps = app_labels
        else:
            apps = [app for app in settings.INSTALLED_APPS \
                    if not app.startswith('plugins.')] + ['merengue']

        print "Traversing apps: %s" % get_text_list(apps, 'and')
        for app in apps:
            self.handle_app(app, **options)

        # This mapping collects files that may be copied.  Keys are what the
        # file's path relative to `media_root` will be when copied.  Values
        # are a list of 2-tuples containing the the name of the app providing
        # the file and the file's absolute path.  The list will have a length
        # greater than 1 if multiple apps provide a media file with the same
        # relative path.

        # Forget the unused versions of a media file
        for f in self.media_files:
            self.media_files[f] = dict(self.media_files[f]).items()

        # Stop if no media files were found
        if not self.media_files:
            print "\nNo media found."
            return

        interactive = options.get('interactive', False)
        # Try to copy in some predictable order.
        for destination in sorted(self.media_files):
            sources = self.media_files[destination]
            first_source, other_sources = sources[0], sources[1:]
            if interactive and other_sources:
                first_app = first_source[0]
                app_sources = dict(sources)
                for (app, source) in sources:
                    if destination.startswith(app):
                        first_app = app
                        first_source = (app, source)
                        break
                print "\nThe file %r is provided by multiple apps:" % destination
                print "\n".join(["    %s" % app for (app, source) in sources])
                message = "Enter the app that should provide this file [%s]: " % first_app
                while True:
                    app = raw_input(message)
                    if not app:
                        app, source = first_source
                        break
                    elif app in app_sources:
                        source = app_sources[app]
                        break
                    else:
                        print "The app %r does not provide this file." % app
            else:
                app, source = first_source
            print "\nSelected %r provided by %r." % (destination, app)
            self.process_file(source, destination, media_root, **options)

    def handle_app(self, app, **options):
        exclude = options.get('exclude')
        app_label = app.split('.')[-1]
        app_module = import_module(app)
        app_root = os.path.dirname(app_module.__file__)
        app_media = os.path.join(app_root, 'media')
        link = options.get('link')
        if os.path.isdir(app_media):
            self.add_media_files(app_label, app_media, exclude, link)

    def add_media_files(self, app, location, exclude, link):
        prefix_length = len(location) + len(os.sep)
        if link:
            # only links to media folder in every app
            self.media_files.setdefault(
                    app, []).append((app, location))
        else:
            # walk into app media directory to copy every file
            for root, dirs, files in os.walk(location, topdown=True):
                # Filter files and dirs based on the exclusion pattern.
                dirs[:] = self.filter_names(dirs, exclude=exclude)
                for filename in self.filter_names(files, exclude=exclude):
                    absolute_path = os.path.join(root, filename)
                    relative_path = os.path.join(app, absolute_path[prefix_length:])
                    self.media_files.setdefault(
                        relative_path, []).append((app, absolute_path))

    def process_file(self, source, destination, root, link=False, **options):
        dry_run = options.get('dry_run', False)
        interactive = options.get('interactive', False)
        destination = os.path.abspath(os.path.join(root, destination))
        if not dry_run:
            # Get permission bits and ownership of `root`.
            try:
                root_stat = os.stat(root)
            except os.error:
                mode = 0777  # Default for `os.makedirs` anyway.
                uid = gid = None
            else:
                mode = root_stat.st_mode
                uid, gid = root_stat.st_uid, root_stat.st_gid
            destination_dir = os.path.dirname(destination)
            try:
                # Recursively create all the required directories, attempting
                # to use the same mode as `root`.
                os.makedirs(destination_dir, mode)
            except os.error:
                # This probably just means the leaf directory already exists,
                # but if not, we'll find out when copying or linking anyway.
                pass
            else:
                if None not in (uid, gid) and hasattr(os, 'lchown'):
                    os.lchown(destination_dir, uid, gid)
        if link:
            success = self.link_file(source, destination, interactive, dry_run)
        else:
            success = self.copy_file(source, destination, interactive, dry_run)
        if success and None not in (uid, gid) and hasattr(os, 'lchown'):
            # Try to use the same ownership as `root`.
            os.lchown(destination, uid, gid)

    def copy_file(self, source, destination, interactive=False, dry_run=False):
        """Attempt to copy `source` to `destination` and return True if successful.
        Don't remove the file if the destination and source files are the same."""
        if interactive:
            exists = os.path.exists(destination) or os.path.islink(destination)
            if exists:
                print "The file %r already exists." % destination
                if not self.prompt_overwrite(destination):
                    return False
        print "Copying %r to %r." % (source, destination)
        if not dry_run:
            if os.path.realpath(destination) != os.path.realpath(source):
                try:
                    os.remove(destination)
                except os.error:
                    pass
                shutil.copy2(source, destination)
                return True
            else:
                print "The file %r is both the source and destination." % destination,
                print "It won't be modified."
        return False

    def link_file(self, source, destination, interactive=False, dry_run=False):
        "Attempt to link to `source` from `destination` and return True if successful."
        if sys.platform == 'win32':
            message = "Linking is not supported by this platform (%s), please use a real OS."
            raise os.error(message % sys.platform)
        if interactive:
            exists = os.path.exists(destination) or os.path.islink(destination)
            if exists:
                print "The file %r already exists." % destination
                if not self.prompt_overwrite(destination):
                    return False
        if not dry_run:
            try:
                # unlink the destination before actually linking the source again
                os.remove(destination)
            except os.error:
                pass
            print "Linking to %r from %r." % (source, destination)
            os.symlink(source, destination)
            return True
        return False

    def prompt_overwrite(self, filename, default=True):
        "Prompt the user to overwrite and return their selection as True or False."
        yes_values = ['Y']
        no_values = ['N']
        if default:
            prompt = "Overwrite? [Y/n]: "
            yes_values.append('')
        else:
            prompt = "Overwrite? [y/N]: "
            no_values.append('')
        while True:
            overwrite = raw_input(prompt).strip().upper()
            if overwrite in yes_values:
                return True
            elif overwrite in no_values:
                return False
            else:
                print "Select 'Y' or 'N'."

    def filter_names(self, names, exclude=None, func=glob.fnmatch.filter):
        if exclude is None:
            exclude = []
        elif isinstance(exclude, basestring):
            exclude = exclude.split()
        else:
            exclude = [pattern for patterns in exclude for pattern in patterns.split()]
        excluded_names = set(
            [name for pattern in exclude for name in func(names, pattern)])
        return sorted(set(names) - excluded_names)
