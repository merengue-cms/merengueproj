from django.db import transaction

from merengue.theme import get_theme_dirs
from merengue.theme.models import Theme


def check_themes():
    """ check themes found in file system and compare with registered one in database """
    # all process will be in a unique transaction, we don't want to get self committed
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
    except:
        transaction.savepoint_rollback(sid)
        raise
    else:
        transaction.savepoint_commit(sid)
