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

from django.db import transaction

from merengue.theming import get_theme_dirs
from merengue.theming.models import Theme


def check_themes():
    """ 
    check themes found in file system and compare with registered one in
    database 
    """
    
#    all process will be in a unique transaction, we don't want to get 
#    self committed
#@FIXME: Probably we should delete non-existing themes from database.
    sid = transaction.savepoint()
    try:
        # first disable all themes
        Theme.objects.all().update(installed=False)
        # now look for all themes in filesystem and enable them
        for theme_dir, theme_path in get_theme_dirs():
            theme, created = Theme.objects.get_or_create(directory_name=theme_dir)
            theme.update_from_fs(commit=False)
            theme.installed = True
            theme.save()            
        try:
            Theme.objects.active()
        except Theme.DoesNotExist:
            # merengue theme will be the active by default if not exists
            Theme.objects.filter(name='merengue').update(active=True)
    except:
        transaction.savepoint_rollback(sid)
        raise
    else:
        transaction.savepoint_commit(sid)
