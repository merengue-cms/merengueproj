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

from functools import wraps
# django imports
from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.contrib.auth.models import User, AnonymousUser, Group
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.template import defaultfilters
from django.utils.decorators import available_attrs

# merengue imports
from merengue.cache import memoize, MemoizeCache
from merengue.perms import ANONYMOUS_ROLE_SLUG, PARTICIPANT_ROLE_SLUG, OWNER_ROLE_SLUG
from merengue.perms.exceptions import PermissionDenied
from merengue.perms.models import ObjectPermission
from merengue.perms.models import ObjectPermissionInheritanceBlock
from merengue.perms.models import Permission
from merengue.perms.models import PrincipalRoleRelation
from merengue.perms.models import Role

MANAGE_SITE_PERMISION = 'manage_site'
MANAGE_USER_PERMISION = 'manage_user'
MANAGE_MULTIMEDIA_PERMISSION = 'manage_multimedia'
MANAGE_PLUGIN_PERMISSION = 'manage_plugin_content'
MANAGE_BLOCK_PERMISSION = 'manage_block'
MANAGE_CACHE_INVALIDATION_PERMISSION = 'cache_invalidation'


# Cache stuff  #################################################################

PERMS_CACHE_KEY = 'perms_cache'


class RolesCache(MemoizeCache):

    def clear(self, users_to_clear):
        for k, v in self._cache.items():
            if k[0] in users_to_clear:
                del self._cache[k]
        cache.set(self.cache_prefix, self._cache)

_roles_cache = RolesCache('roles_cache')


def clear_roles_cache(principal):
    if isinstance(principal, User):
        users_to_clear = [principal]
    else:
        users_to_clear = principal.user_set.all()
    if users_to_clear:
        _roles_cache.clear(users_to_clear)


def get_from_cache(user, content, codename, roles):
    if not settings.CACHE_PERMISSIONS:
        return None
    perms_cache = cache.get(PERMS_CACHE_KEY)
    if perms_cache is None:
        return None
    roles_value = roles and tuple(r.id for r in roles) or None
    return perms_cache.get(
        (user.id, content, str(codename), roles_value),
        None,
    )


def clear_cache():
    cache.set(PERMS_CACHE_KEY, {})


def set_permission_in_cache(global_perm=False):
    """
    Decorator for views makes store in cache after doing the logic
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_func(*args, **kwargs):
            has_permission = view_func(*args, **kwargs)
            if isinstance(has_permission, tuple):
                # a tuple (has_permission, "cached") has been returned
                # this implies the permission was cached and there is no need
                # to update cache again
                return has_permission[0]
            if not settings.CACHE_PERMISSIONS:
                return has_permission
            # update the permission cache
            cache_values = {}
            if global_perm:
                cache_params = ('user', 'codename', 'roles')
            else:
                cache_params = ('content', 'user', 'codename', 'roles')
            args_len = len(args)
            for i, param in enumerate(cache_params):
                if i < args_len:
                    cache_values[param] = args[i]
                else:  # is in kwargs
                    cache_values[param] = kwargs.get(param, None)
            if global_perm:
                cache_values['content'] = None
            perms_cache = cache.get(PERMS_CACHE_KEY, {})
            roles = cache_values['roles'] and tuple(r.id for r in cache_values['roles']) or None
            cache_key = (
                getattr(cache_values['user'], 'id', None),
                getattr(cache_values['content'], 'id', None),
                str(cache_values['codename']),
                roles,
            )
            perms_cache[cache_key] = has_permission
            cache.set(PERMS_CACHE_KEY, perms_cache)
            return has_permission
        return _wrapped_func
    return decorator


# Roles ######################################################################


def add_role(principal, role):
    """Adds a global role to a principal.

    **Parameters:**

    principal
        The principal (user or group) which gets the role added.

    role
        The role which is assigned.
    """
    clear_cache()
    clear_roles_cache(principal)
    if isinstance(principal, User):
        try:
            PrincipalRoleRelation.objects.get(user=principal, role=role, content__isnull=True)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(user=principal, role=role)
            return True
    else:
        try:
            PrincipalRoleRelation.objects.get(group=principal, role=role, content__isnull=True)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(group=principal, role=role)
            return True
    return False


def add_local_role(obj, principal, role):
    """Adds a local role to a principal.

    **Parameters:**

    obj
        The object for which the principal gets the role.

    principal
        The principal (user or group) which gets the role.

    role
        The role which is assigned.
    """
    clear_cache()
    clear_roles_cache(principal)
    if isinstance(principal, User):
        try:
            PrincipalRoleRelation.objects.get(user=principal, role=role, content=obj)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(user=principal, role=role, content=obj)
            return True
    else:
        try:
            PrincipalRoleRelation.objects.get(group=principal, role=role, content=obj)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(group=principal, role=role, content=obj)
            return True

    return False


def remove_role(principal, role):
    """Removes role from passed principal.

    **Parameters:**

    principal
        The principal (user or group) from which the role is removed.

    role
        The role which is removed.
    """
    clear_cache()
    clear_roles_cache(principal)
    try:
        if isinstance(principal, User):
            ppr = PrincipalRoleRelation.objects.get(
                    user=principal, role=role, content__isnull=True)
        else:
            ppr = PrincipalRoleRelation.objects.get(
                    group=principal, role=role, content__isnull=True)

    except PrincipalRoleRelation.DoesNotExist:
        return False
    else:
        ppr.delete()

    return True


def remove_local_role(obj, principal, role):
    """Removes role from obj and principle.

    **Parameters:**

    obj
        The object from which the role is removed.

    principal
        The principal (user or group) from which the role is removed.

    role
        The role which is removed.
    """
    clear_cache()
    clear_roles_cache(principal)
    try:
        if isinstance(principal, User):
            ppr = PrincipalRoleRelation.objects.get(
                user=principal, role=role, content=obj)
        else:
            ppr = PrincipalRoleRelation.objects.get(
                group=principal, role=role, content=obj)

    except PrincipalRoleRelation.DoesNotExist:
        return False
    else:
        ppr.delete()

    return True


def remove_roles(principal):
    """Removes all roles passed principal (user or group).

    **Parameters:**

    principal
        The principal (user or group) from which all roles are removed.
    """
    clear_cache()
    clear_roles_cache(principal)
    if isinstance(principal, User):
        ppr = PrincipalRoleRelation.objects.filter(
            user=principal, content__isnull=True)
    else:
        ppr = PrincipalRoleRelation.objects.filter(
            group=principal, content__isnull=True)

    if ppr:
        ppr.delete()
        return True
    else:
        return False


def remove_local_roles(obj, principal):
    """Removes all local roles from passed object and principal (user or
    group).

    **Parameters:**

    obj
        The object from which the roles are removed.

    principal
        The principal (user or group) from which the roles are removed.
    """
    clear_cache()
    clear_roles_cache(principal)
    if isinstance(principal, User):
        ppr = PrincipalRoleRelation.objects.filter(
            user=principal, content=obj)
    else:
        ppr = PrincipalRoleRelation.objects.filter(
            group=principal, content=obj)

    if ppr:
        ppr.delete()
        return True
    else:
        return False


def _get_roles(user, obj=None):
    """Returns all roles of passed user for passed content object. This takes
    direct and roles via a group into account. If an object is passed local
    roles will also added.

    **Parameters:**

    obj
        The object from which the roles are returned.

    user
        The user from which the roles are returned.
    """
    if isinstance(user, AnonymousUser):
        return Role.objects.filter(slug=ANONYMOUS_ROLE_SLUG)

    role_ids = []
    groups = user.groups.all()
    groups_ids_str = ", ".join([str(g.id) for g in groups])

    # Gobal roles for user and the user's groups
    cursor = connection.cursor()

    if groups_ids_str:
        cursor.execute("""SELECT role_id
                          FROM perms_principalrolerelation
                          WHERE (user_id=%s OR group_id IN (%s))
                          AND content_id is Null""" % (user.id, groups_ids_str))
    else:
        cursor.execute("""SELECT role_id
                          FROM perms_principalrolerelation
                          WHERE user_id=%s
                          AND content_id is Null""" % user.id)

    for row in cursor.fetchall():
        role_ids.append(row[0])

    # Local roles for user and the user's groups and all ancestors of the
    # passed object.
    while obj:
        if groups_ids_str:
            cursor.execute("""SELECT role_id
                              FROM perms_principalrolerelation
                              WHERE (user_id='%s' OR group_id IN (%s))
                              AND content_id='%s'""" % (user.id, groups_ids_str, obj.id))
        else:
            cursor.execute("""SELECT role_id
                              FROM perms_principalrolerelation
                              WHERE user_id='%s'
                              AND content_id='%s'""" % (user.id, obj.id))

        for row in cursor.fetchall():
            role_ids.append(row[0])

        get_owners = getattr(obj, 'get_owners', None)
        get_participants = getattr(obj, 'get_participants', None)
        if get_owners and callable(get_owners) and user in obj.get_owners():
            role_ids.append(Role.objects.get(slug=OWNER_ROLE_SLUG).id)

        if get_participants and callable(get_participants) and user in obj.get_participants():
            role_ids.append(Role.objects.get(slug=PARTICIPANT_ROLE_SLUG).id)

        try:
            obj = obj.get_parent_for_permissions()
        except AttributeError:
            obj = None

    return Role.objects.filter(pk__in=role_ids)
get_roles = memoize(_get_roles, _roles_cache, 2)


def get_global_roles(principal):
    """Returns global roles of passed principal (user or group).
    """
    if isinstance(principal, AnonymousUser):
        return Role.objects.filter(slug=ANONYMOUS_ROLE_SLUG)
    if isinstance(principal, User):
        return [prr.role for prr in PrincipalRoleRelation.objects.filter(
            user=principal, content__isnull=True)]
    else:
        return [prr.role for prr in PrincipalRoleRelation.objects.filter(
            group=principal, content__isnull=True)]


def get_local_roles(obj, principal):
    """Returns local for passed user and content object.
    """
    if isinstance(principal, User):
        roles = [prr.role for prr in PrincipalRoleRelation.objects.filter(
            user=principal, content=obj)]

        if principal in obj.get_owners():
            roles.append(Role.objects.get(slug=OWNER_ROLE_SLUG))

        if principal in obj.get_participants():
            roles.append(Role.objects.get(slug=PARTICIPANT_ROLE_SLUG))
        return roles
    else:
        return [prr.role for prr in PrincipalRoleRelation.objects.filter(
            group=principal, content=obj)]


def get_all_local_roles(obj):
    roles = []
    for relation in PrincipalRoleRelation.objects.filter(content=obj):
        if relation.user:
            roles.append((relation.user, relation.role))
        elif relation.group:
            roles.append((relation.group, relation.role))
        else:
            continue
    owner_role = Role.objects.get(slug=OWNER_ROLE_SLUG)
    for principal in obj.get_owners():
        roles.append((principal, owner_role))
    participant_role = Role.objects.get(slug=PARTICIPANT_ROLE_SLUG)
    for principal in obj.get_participants():
        roles.append((principal, participant_role))
    return roles


# Permissions ################################################################


def grant_permission(role, permission, obj=None):
    """Grants passed permission to passed role. Returns True if the permission
    was able to be added, otherwise False.

    **Parameters:**

    role
        The role for which the permission should be granted.

    permission
        The permission which should be granted. Either a permission
        object or the codename of a permission.

    obj
        The content object for which the permission should be granted.
        If obj is None, the permissions should be granted for all contents.

    """
    clear_cache()
    if not isinstance(permission, Permission):
        try:
            permission = Permission.objects.get(codename=permission)
        except Permission.DoesNotExist:
            return False

    try:
        ObjectPermission.objects.get(role=role, content=obj, permission=permission)
    except ObjectPermission.DoesNotExist:
        ObjectPermission.objects.create(role=role, content=obj, permission=permission)

    return True


def remove_permission(role, permission, obj=None):
    """Removes passed permission from passed role and object. Returns True if
    the permission has been removed.

    **Parameters:**

    obj
        The content object for which a permission should be removed.
        If obj is None, the permissions should be removed for all contents.

    role
        The role for which a permission should be removed.

    permission
        The permission which should be removed. Either a permission object
        or the codename of a permission.
    """
    clear_cache()
    if not isinstance(permission, Permission):
        try:
            permission = Permission.objects.get(codename=permission)
        except Permission.DoesNotExist:
            return False

    try:
        op = ObjectPermission.objects.get(role=role, content=obj, permission=permission)
    except ObjectPermission.DoesNotExist:
        return False

    op.delete()
    return True


@set_permission_in_cache(global_perm=True)
def has_global_permission(user, codename, roles=None):
    """Checks whether the passed user has passed permission for passed object.

    **Parameters:**

    codename
        The permission's codename which should be checked.

    user
        The user for which the permission should be checked.

    roles
        If given these roles will be assigned to the user temporarily before
        the permissions are checked.
    """

    if user.is_superuser:
        return True

    # try to get from cache
    cached_perm = get_from_cache(user, None, codename, roles)
    if cached_perm is not None:
        return cached_perm, "cached"  # latest returned value never will reach the function which makes call

    if roles is None:
        roles = []

    # we check first ANONYMOUS_ROLE_SLUG to reduce SQL sentences and improve
    # cache hit percentage (next sentence is more susceptible to be cached)
    p_anon = ObjectPermission.objects.filter(
        Q(content__isnull=True, role__slug=ANONYMOUS_ROLE_SLUG, permission__codename=codename))

    if p_anon:
        return True

    if not user.is_anonymous():
        roles.extend(get_roles(user))

    p = ObjectPermission.objects.filter(
        Q(content__isnull=True, role__in=roles, permission__codename=codename))

    if p:
        return True

    return False


@set_permission_in_cache()
def has_permission(obj, user, codename, roles=None):
    """Checks whether the passed user has passed permission for passed object.

    **Parameters:**

    obj
        The object for which the permission should be checked.

    codename
        The permission's codename which should be checked.

    user
        The user for which the permission should be checked.

    roles
        If given these roles will be assigned to the user temporarily before
        the permissions are checked.
    """

    if user.is_superuser:
        return True

    # try to get from cache
    cached_perm = get_from_cache(user, obj, codename, roles)
    if cached_perm is not None:
        return cached_perm, "cached"  # latest returned value never will reach the function which makes call

    if roles is None:
        roles = []

    roles.append(Role.objects.get(slug=ANONYMOUS_ROLE_SLUG))

    global_perm = has_global_permission(user, codename, roles)
    if not obj or (obj and getattr(obj, 'adquire_global_permissions', True) and global_perm):
        # returns global_perm if there is not an object or there is an object
        # which adquire global permissions and global_perm is True and there is
        # not need to further processing
        return global_perm

    if not can_use_permissions(obj):
        # object does not support permissions
        return False

    if user.is_anonymous():
        user = None
    else:
        roles.extend(get_roles(user, obj))

    while obj is not None:
        # if obj doesn't support permissions, use related basecontent
        if getattr(obj, 'adquire_global_permissions', None) is None:
            try:
                obj = obj.basecontent_set.all()[0]
            except AttributeError:
                return False
            except IndexError:
                return False

        filters = Q(content=obj, role__in=roles, permission__codename=codename)
        p = ObjectPermission.objects.filter(filters)

        if p:
            return True

        if is_inherited(obj, codename) == False:
            return False

        try:
            obj = obj.get_parent_for_permissions()
        except AttributeError:
            return False

    return False


def has_permission_in_queryset(queryset, user, codename, roles=None):
    """Checks whether the passed user has passed permission for passed object.

    **Parameters:**

    queryset
        The queryset for which the permission should be checked.

    codename
        The permission's codename which should be checked.

    user
        The user for which the permission should be checked.

    roles
        If given these roles will be assigned to the user temporarily before
        the permissions are checked.
    """
    for obj in queryset:
        if not has_permission(obj, user, codename, roles):
            return False
    return True


def assert_has_permission(obj, user, codename, roles=None):
    if not has_permission(obj, user, codename, roles):
        raise PermissionDenied(content=obj, user=user, perm=codename)
    return True


def assert_has_global_permission(user, codename, roles=None):
    if not has_global_permission(user, codename, roles):
        raise PermissionDenied(user=user, perm=codename)
    return True


def assert_has_permission_in_queryset(queryset, user, codename, roles=None):
    for obj in queryset:
        if not has_permission(obj, user, codename, roles):
            raise PermissionDenied(content=obj, user=user, perm=codename)
    return True


def can_use_permissions(obj):
    """ The obj can contains permissions """
    from merengue.base.models import BaseContent
    return isinstance(obj, BaseContent)

# Inheritance ################################################################


def add_inheritance_block(obj, permission):
    """Adds an inheritance for the passed permission on the passed obj.

    **Parameters:**

        permission
            The permission for which an inheritance block should be added.
            Either a permission object or the codename of a permission.
        obj
            The content object for which an inheritance block should be added.
    """
    if not isinstance(permission, Permission):
        try:
            permission = Permission.objects.get(codename=permission)
        except Permission.DoesNotExist:
            return False

    try:
        ObjectPermissionInheritanceBlock.objects.get(content=obj, permission=permission)
    except ObjectPermissionInheritanceBlock.DoesNotExist:
        result, created = ObjectPermissionInheritanceBlock.objects.get_or_create(content=obj, permission=permission)
        if not created:
            return False
    return True


def remove_inheritance_block(obj, permission):
    """Removes a inheritance block for the passed permission from the passed
    object.

    **Parameters:**

        obj
            The content object for which an inheritance block should be added.

        permission
            The permission for which an inheritance block should be removed.
            Either a permission object or the codename of a permission.
    """
    if not isinstance(permission, Permission):
        try:
            permission = Permission.objects.get(codename=permission)
        except Permission.DoesNotExist:
            return False

    try:
        opi = ObjectPermissionInheritanceBlock.objects.get(content=obj, permission=permission)
    except ObjectPermissionInheritanceBlock.DoesNotExist:
        return False

    opi.delete()
    return True


def is_inherited(obj, codename):
    """Returns True if the passed permission is inherited for passed object.

    **Parameters:**

        obj
            The content object for which the permission should be checked.

        codename
            The permission which should be checked. Must be the codename of
            the permission.
    """
    try:
        ObjectPermissionInheritanceBlock.objects.get(
            content=obj, permission__codename=codename)
    except ObjectDoesNotExist:
        return True
    else:
        return False


def can_manage_site(user):
    return has_global_permission(user, MANAGE_SITE_PERMISION)


def can_manage_user(user):
    return has_global_permission(user, MANAGE_USER_PERMISION)


def can_manage_multimedia(user):
    return has_global_permission(user, MANAGE_MULTIMEDIA_PERMISSION)


def can_manage_plugin_content(user):
    return has_global_permission(user, MANAGE_PLUGIN_PERMISSION)


def assert_manage_site(user):
    if not has_global_permission(user, MANAGE_SITE_PERMISION):
        raise PermissionDenied(user=user, perm=MANAGE_SITE_PERMISION)
    return True


def assert_manage_user(user):
    if not has_global_permission(user, MANAGE_USER_PERMISION):
        raise PermissionDenied(user=user, perm=MANAGE_SITE_PERMISION)
    return True


def assert_manage_multimedia(user):
    if not has_global_permission(user, MANAGE_MULTIMEDIA_PERMISSION):
        raise PermissionDenied(user=user, perm=MANAGE_SITE_PERMISION)
    return True


def assert_manage_plugin_content(user):
    if not has_global_permission(user, MANAGE_PLUGIN_PERMISSION):
        raise PermissionDenied(user=user, perm=MANAGE_SITE_PERMISION)
    return True


def get_group(id):
    """Returns the group with passed id or None.
    """
    try:
        return Group.objects.get(pk=id)
    except Group.DoesNotExist:
        return None


def get_role(id):
    """Returns the role with passed id or None.
    """
    try:
        return Role.objects.get(pk=id)
    except Role.DoesNotExist:
        return None


def get_user(id):
    """Returns the user with passed id or None.
    """
    try:
        return User.objects.get(pk=id)
    except User.DoesNotExist:
        return None


def reset(obj):
    """Resets all permissions and inheritance blocks of passed object.
    """
    ObjectPermissionInheritanceBlock.objects.filter(content=obj).delete()
    ObjectPermission.objects.filter(content=obj).delete()


# Registering ################################################################


def register_permission(name, codename, for_models=None, ctypes=None, builtin=False):
    """Registers a permission to the framework. Returns the permission if the
    registration was successfully, otherwise False.

    **Parameters:**

        name
            The unique name of the permission. This is displayed to the
            customer.
        codename
            The unique codename of the permission. This is used internally to
            identify the permission.
        for_models
            It's complementary to The models for which the permission is active.
            This can be used to display only reasonable permissions for an object.
        ctypes
            The content type for which the permission is active. This can be
            used to display only reasonable permissions for an object.
        builtin
            A builtin permission will appears in the manage permission view of
            every content. Will be False by default.
    """
    if for_models and ctypes:
        raise ImproperlyConfigured("You cannot call register_permission both with ctypes and models parameters")
    if for_models is not None:
        ctypes = [ContentType.objects.get_for_model(model) for model in for_models]
    if ctypes is None:
        ctypes = []

    perms = Permission.objects.filter(Q(name=name) | Q(codename=codename))
    if perms.count() > 0:
        return False

    p = Permission.objects.create(name=name, codename=codename, builtin=builtin)
    p.content_types = ctypes
    p.save()
    return p


def unregister_permission(codename):
    """Unregisters a permission from the framework

    **Parameters:**

        codename
            The unique codename of the permission.
    """
    try:
        permission = Permission.objects.get(codename=codename)
    except Permission.DoesNotExist:
        return False
    permission.delete()
    return True


def register_role(name, slug=None):
    """Registers a role with passed name to the framework. Returns the new
    role if the registration was successfully, otherwise False.

    **Parameters:**

    name
        The unique role name.
    slug
        The role slug.
    """
    if slug is None:
        slug = defaultfilters.slugify(name)
    role, created = Role.objects.get_or_create(name=name, slug=slug)
    if created:
        return role
    return False


def unregister_role(name):
    """Unregisters the role with passed name.

    **Parameters:**

    name
        The unique role name.
    """
    try:
        role = Role.objects.get(name=name)
    except Role.DoesNotExist:
        return False

    role.delete()
    return True


def register_group(name):
    """Registers a group with passed name to the framework. Returns the new
    group if the registration was successfully, otherwise False.

    Actually this creates just a default Django Group.

    **Parameters:**

    name
        The unique group name.
    """
    group, created = Group.objects.get_or_create(name=name)
    if created:
        return group
    return False


def unregister_group(name):
    """Unregisters the group with passed name. Returns True if the
    unregistration was succesfull otherwise False.

    Actually this deletes just a default Django Group.

    **Parameters:**

    name
        The unique role name.
    """
    try:
        group = Group.objects.get(name=name)
    except Group.DoesNotExist:
        return False

    group.delete()
    return True
