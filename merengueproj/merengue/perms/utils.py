# django imports
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured

# permissions imports
from merengue.perms.models import ObjectPermission
from merengue.perms.models import ObjectPermissionInheritanceBlock
from merengue.perms.models import Permission
from merengue.perms.models import PrincipalRoleRelation
from merengue.perms.models import Role

# Roles ######################################################################


def add_role(principal, role):
    """Adds a global role to a principal.

    **Parameters:**

    principal
        The principal (user or group) which gets the role added.

    role
        The role which is assigned.
    """
    if isinstance(principal, User):
        try:
            ppr = PrincipalRoleRelation.objects.get(user=principal, role=role, content__isnull=True)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(user=principal, role=role)
            return True
    else:
        try:
            ppr = PrincipalRoleRelation.objects.get(group=principal, role=role, content__isnull=True)
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
    ctype = ContentType.objects.get_for_model(obj)
    if isinstance(principal, User):
        try:
            ppr = PrincipalRoleRelation.objects.get(user=principal, role=role, content=obj)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(user=principal, role=role, content=obj)
            return True
    else:
        try:
            ppr = PrincipalRoleRelation.objects.get(group=principal, role=role, content=obj)
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
    try:
        ctype = ContentType.objects.get_for_model(obj)

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
    ctype = ContentType.objects.get_for_model(obj)

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


def get_roles(principal, obj=None):
    """Returns all roles of passed user for passed content object. This takes
    direct and roles via a group into account. If an object is passed local
    roles will also added.

    **Parameters:**

    obj
        The object from which the roles are removed.

    principal
        The principal (user or group) from which the roles are removed.
    """
    roles = get_global_roles(principal)

    if obj is not None:
        roles.extend(get_local_roles(obj, principal))

    if isinstance(principal, User):
        for group in principal.groups.all():
            roles.extend(get_local_roles(obj, group))
            roles.extend(get_roles(group))

    return roles


def get_global_roles(principal):
    """Returns global roles of passed principal (user or group).
    """
    if isinstance(principal, User):
        return [prr.role for prr in PrincipalRoleRelation.objects.filter(
            user=principal, content__isnull=True)]
    else:
        return [prr.role for prr in PrincipalRoleRelation.objects.filter(
            group=principal, content__isnull=True)]


def get_local_roles(obj, principal):
    """Returns local for passed user and content object.
    """
    ctype = ContentType.objects.get_for_model(obj)

    if isinstance(principal, User):
        return [prr.role for prr in PrincipalRoleRelation.objects.filter(
            user=principal, content=obj)]
    else:
        return [prr.role for prr in PrincipalRoleRelation.objects.filter(
            group=principal, content=obj)]


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
    if not isinstance(permission, Permission):
        try:
            permission = Permission.objects.get(codename = permission)
        except Permission.DoesNotExist:
            return False

    if obj:
        ct = ContentType.objects.get_for_model(obj)
    try:
        ObjectPermission.objects.get(role=role, content=obj, permission=permission)
    except ObjectPermission.DoesNotExist:
        ObjectPermission.objects.create(role=role, content=obj, permission=permission)

    return True


def remove_permission(obj, role, permission):
    """Removes passed permission from passed role and object. Returns True if
    the permission has been removed.

    **Parameters:**

    obj
        The content object for which a permission should be removed.

    role
        The role for which a permission should be removed.

    permission
        The permission which should be removed. Either a permission object
        or the codename of a permission.
    """
    if not isinstance(permission, Permission):
        try:
            permission = Permission.objects.get(codename = permission)
        except Permission.DoesNotExist:
            return False

    ct = ContentType.objects.get_for_model(obj)

    try:
        op = ObjectPermission.objects.get(role=role, content=obj, permission = permission)
    except ObjectPermission.DoesNotExist:
        return False

    op.delete()
    return True


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
    if roles is None:
        roles = []

    if user.is_superuser:
        return True

    if user.is_anonymous():
        user = None
    else:
        roles.extend(get_roles(user, obj))

    ct = ContentType.objects.get_for_model(obj)

    while obj is not None:
        p = ObjectPermission.objects.filter(
            Q(content=obj, role__in=roles, permission__codename=codename) |
            Q(content__isnull=True, role__in=roles, permission__codename=codename))

        if p.count() > 0:
            return True

        if is_inherited(obj, codename) == False:
            return False

        try:
            obj = obj.get_parent_for_permissions()
            ct = ContentType.objects.get_for_model(obj)
        except AttributeError:
            return False

    return False


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
            permission = Permission.objects.get(codename = permission)
        except Permission.DoesNotExist:
            return False

    ct = ContentType.objects.get_for_model(obj)
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
            permission = Permission.objects.get(codename = permission)
        except Permission.DoesNotExist:
            return False

    ct = ContentType.objects.get_for_model(obj)
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
    ct = ContentType.objects.get_for_model(obj)
    try:
        ObjectPermissionInheritanceBlock.objects.get(
            content=obj, permission__codename = codename)
    except ObjectDoesNotExist:
        return True
    else:
        return False


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
    ctype = ContentType.objects.get_for_model(obj)
    ObjectPermissionInheritanceBlock.objects.filter(content=obj).delete()
    ObjectPermission.objects.filter(content=obj).delete()


# Registering ################################################################


def register_permission(name, codename, ctypes=None, for_models=None, builtin=False):
    """Registers a permission to the framework. Returns the permission if the
    registration was successfully, otherwise False.

    **Parameters:**

        name
            The unique name of the permission. This is displayed to the
            customer.
        codename
            The unique codename of the permission. This is used internally to
            identify the permission.
        ctypes
            The content type for which the permission is active. This can be
            used to display only reasonable permissions for an object.
        for_models
            It's complementary to The models for which the permission is active.
            This can be used to display only reasonable permissions for an object.
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


def register_role(name):
    """Registers a role with passed name to the framework. Returns the new
    role if the registration was successfully, otherwise False.

    **Parameters:**

    name
        The unique role name.
    """
    role, created = Role.objects.get_or_create(name=name)
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
