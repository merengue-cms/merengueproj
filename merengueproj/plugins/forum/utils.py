from merengue.perms.utils import has_permission


def can_create_new_thread(user, content):
    return user and has_permission(content, user, 'create_new_thread') or False
