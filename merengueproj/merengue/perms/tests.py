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

# django imports
from django.conf import settings
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.client import Client

from merengue.base.models import BaseContent
from merengue.section.models import BaseSection, SectionRelatedContent
from merengue.perms import ANONYMOUS_ROLE_SLUG
from merengue.perms.models import Permission
from merengue.perms.models import ObjectPermission
from merengue.perms.models import ObjectPermissionInheritanceBlock
from merengue.perms.models import Role

import merengue.perms.utils


class RoleTestCase(TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.role_1 = merengue.perms.utils.register_role("Role 1")
        self.role_2 = merengue.perms.utils.register_role("Role 2")

        self.user = User.objects.create(username="john")
        self.group = Group.objects.create(name="brights")

        self.page_1 = BaseContent.objects.create(slug="page-1", name_en="Page 1")
        self.page_2 = BaseContent.objects.create(slug="page-2", name_en="Page 2")
        self.section = BaseSection.objects.create(slug="section", name_en="Section")

    def test_getter(self):
        """
        """
        result = merengue.perms.utils.get_group(self.group.id)
        self.assertEqual(result, self.group)

        result = merengue.perms.utils.get_group(42)
        self.assertEqual(result, None)

        result = merengue.perms.utils.get_role(self.role_1.id)
        self.assertEqual(result, self.role_1)

        result = merengue.perms.utils.get_role(42)
        self.assertEqual(result, None)

        result = merengue.perms.utils.get_user(self.user.id)
        self.assertEqual(result, self.user)

        result = merengue.perms.utils.get_user(42)
        self.assertEqual(result, None)

    def test_global_roles_user(self):
        """
        """
        # Add role 1
        result = merengue.perms.utils.add_role(self.user, self.role_1)
        self.assertEqual(result, True)

        # Add role 1 again
        result = merengue.perms.utils.add_role(self.user, self.role_1)
        self.assertEqual(result, False)

        result = merengue.perms.utils.get_roles(self.user)
        self.assertEqual(list(result), [self.role_1])

        # Add role 2
        result = merengue.perms.utils.add_role(self.user, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_roles(self.user)
        self.assertEqual(list(result), [self.role_1, self.role_2])

        # Remove role 1
        result = merengue.perms.utils.remove_role(self.user, self.role_1)
        self.assertEqual(result, True)

        # Remove role 1 again
        result = merengue.perms.utils.remove_role(self.user, self.role_1)
        self.assertEqual(result, False)

        result = merengue.perms.utils.get_roles(self.user)
        self.assertEqual(list(result), [self.role_2])

        # Remove role 2
        result = merengue.perms.utils.remove_role(self.user, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_roles(self.user)
        self.assertEqual(list(result), [])

        # AnonymousUser roles
        anon_user = AnonymousUser()
        result = merengue.perms.utils.get_roles(anon_user)
        self.assertEqual(result[0], Role.objects.get(slug=ANONYMOUS_ROLE_SLUG))

    def test_global_roles_group(self):
        """
        """
        # Add role 1
        result = merengue.perms.utils.add_role(self.group, self.role_1)
        self.assertEqual(result, True)

        # Add role 1 again
        result = merengue.perms.utils.add_role(self.group, self.role_1)
        self.assertEqual(result, False)

        result = merengue.perms.utils.get_global_roles(self.group)
        self.assertEqual(result, [self.role_1])

        # Add role 2
        result = merengue.perms.utils.add_role(self.group, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_global_roles(self.group)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove role 1
        result = merengue.perms.utils.remove_role(self.group, self.role_1)
        self.assertEqual(result, True)

        # Remove role 1 again
        result = merengue.perms.utils.remove_role(self.group, self.role_1)
        self.assertEqual(result, False)

        result = merengue.perms.utils.get_global_roles(self.group)
        self.assertEqual(result, [self.role_2])

        # Remove role 2
        result = merengue.perms.utils.remove_role(self.group, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_global_roles(self.group)
        self.assertEqual(result, [])

    def test_remove_roles_user(self):
        """
        """
        # Add role 1
        result = merengue.perms.utils.add_role(self.user, self.role_1)
        self.assertEqual(result, True)

        # Add role 2
        result = merengue.perms.utils.add_role(self.user, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_roles(self.user)
        self.assertEqual(list(result), [self.role_1, self.role_2])

        # Remove roles
        result = merengue.perms.utils.remove_roles(self.user)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_roles(self.user)
        self.assertEqual(list(result), [])

        # Remove roles
        result = merengue.perms.utils.remove_roles(self.user)
        self.assertEqual(result, False)

    def test_remove_roles_group(self):
        """
        """
        # Add role 1
        result = merengue.perms.utils.add_role(self.group, self.role_1)
        self.assertEqual(result, True)

        # Add role 2
        result = merengue.perms.utils.add_role(self.group, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_global_roles(self.group)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove roles
        result = merengue.perms.utils.remove_roles(self.group)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_global_roles(self.group)
        self.assertEqual(result, [])

        # Remove roles
        result = merengue.perms.utils.remove_roles(self.group)
        self.assertEqual(result, False)

    def test_local_role_user(self):
        """
        """
        # Add local role to page 1
        result = merengue.perms.utils.add_local_role(self.page_1, self.user, self.role_1)
        self.assertEqual(result, True)

        # Again
        result = merengue.perms.utils.add_local_role(self.page_1, self.user, self.role_1)
        self.assertEqual(result, False)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.user)
        self.assertEqual(result, [self.role_1])

        # Add local role 2
        result = merengue.perms.utils.add_local_role(self.page_1, self.user, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.user)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove role 1
        result = merengue.perms.utils.remove_local_role(self.page_1, self.user, self.role_1)
        self.assertEqual(result, True)

        # Remove role 1 again
        result = merengue.perms.utils.remove_local_role(self.page_1, self.user, self.role_1)
        self.assertEqual(result, False)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.user)
        self.assertEqual(result, [self.role_2])

        # Remove role 2
        result = merengue.perms.utils.remove_local_role(self.page_1, self.user, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.user)
        self.assertEqual(result, [])

    def test_local_role_group(self):
        """
        """
        # Add local role to page 1
        result = merengue.perms.utils.add_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, True)

        # Again
        result = merengue.perms.utils.add_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, False)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.group)
        self.assertEqual(result, [self.role_1])

        # Add local role 2
        result = merengue.perms.utils.add_local_role(self.page_1, self.group, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.group)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove role 1
        result = merengue.perms.utils.remove_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, True)

        # Remove role 1 again
        result = merengue.perms.utils.remove_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, False)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.group)
        self.assertEqual(result, [self.role_2])

        # Remove role 2
        result = merengue.perms.utils.remove_local_role(self.page_1, self.group, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.group)
        self.assertEqual(result, [])

    def test_remove_local_roles_user(self):
        """
        """
        # Add local role to page 1
        result = merengue.perms.utils.add_local_role(self.page_1, self.user, self.role_1)
        self.assertEqual(result, True)

        # Add local role 2
        result = merengue.perms.utils.add_local_role(self.page_1, self.user, self.role_2)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.user)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove all local roles
        result = merengue.perms.utils.remove_local_roles(self.page_1, self.user)
        self.assertEqual(result, True)

        result = merengue.perms.utils.get_local_roles(self.page_1, self.user)
        self.assertEqual(result, [])

        # Remove all local roles again
        result = merengue.perms.utils.remove_local_roles(self.page_1, self.user)
        self.assertEqual(result, False)

    def test_acquiring_roles(self):
        """
        """
        SectionRelatedContent.objects.create(basesection=self.section, basecontent=self.page_1)
        result = merengue.perms.utils.add_local_role(self.section, self.user, self.role_1)
        self.assertEqual(result, True)
        settings.ACQUIRE_SECTION_ROLES = False
        section_roles = merengue.perms.utils.get_roles(self.user, self.section)
        page_roles = merengue.perms.utils.get_roles(self.user, self.page_1)
        self.assertNotEqual(list(page_roles), list(section_roles))
        settings.ACQUIRE_SECTION_ROLES = True
        merengue.perms.utils._roles_cache.clear([self.user])
        section_roles = merengue.perms.utils.get_roles(self.user, self.section)
        page_roles = merengue.perms.utils.get_roles(self.user, self.page_1)
        self.assertEqual(list(page_roles), list(section_roles))


class PermissionTestCase(TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.role_1 = merengue.perms.utils.register_role("Role 1")
        self.role_2 = merengue.perms.utils.register_role("Role 2")

        self.user = User.objects.create(username="john")
        merengue.perms.utils.add_role(self.user, self.role_1)
        self.user.save()

        self.page_1 = BaseContent.objects.create(slug="page-1", name_en="Page 1")
        self.page_2 = BaseContent.objects.create(slug="page-2", name_en="Page 2")

        self.permission = merengue.perms.utils.register_permission("View permission", "view_perm")

    def test_add_permissions(self):
        """
        """
        # Add per object
        result = merengue.perms.utils.grant_permission(self.role_1, self.permission, self.page_1)
        self.assertEqual(result, True)

        # Add per codename
        result = merengue.perms.utils.grant_permission(self.role_1, "view_perm", self.page_1)
        self.assertEqual(result, True)

        # Add permission which does not exist
        result = merengue.perms.utils.grant_permission(self.role_1, "hurz", self.page_1)
        self.assertEqual(result, False)

        # Add for all objects
        result = merengue.perms.utils.grant_permission(self.role_1, self.permission)
        self.assertEqual(result, True)

    def test_remove_permission(self):
        """
        """
        # Add
        result = merengue.perms.utils.grant_permission(self.role_1, "view_perm", self.page_1)
        self.assertEqual(result, True)

        # Remove
        result = merengue.perms.utils.remove_permission(self.role_1, "view_perm", self.page_1)
        self.assertEqual(result, True)

        # Remove again
        result = merengue.perms.utils.remove_permission(self.role_1, "view_perm", self.page_1)
        self.assertEqual(result, False)

        # Add permission for all contents
        result = merengue.perms.utils.grant_permission(self.role_1, "view_perm")
        self.assertEqual(result, True)

        # Not allowed to remove Object-level permissions if role has global permissions
        result = merengue.perms.utils.remove_permission(self.role_1, "view_perm", self.page_1)
        self.assertEqual(result, False)

        # Remove permission for all contents
        result = merengue.perms.utils.remove_permission(self.role_1, "view_perm")
        self.assertEqual(result, True)

        # Remove again
        result = merengue.perms.utils.remove_permission(self.role_1, "view_perm")
        self.assertEqual(result, False)

    def test_has_permission_role(self):
        """
        """
        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, False)

        result = merengue.perms.utils.grant_permission(self.role_1, self.permission, self.page_1)
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, True)

        result = merengue.perms.utils.remove_permission(self.role_1, "view_perm", self.page_1)
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, False)

    def test_has_permission_all_content(self):

        # Add individual permission
        result = merengue.perms.utils.grant_permission(self.role_1, self.permission, self.page_1)
        self.assertEqual(result, True)

        # Add global permission
        result = merengue.perms.utils.grant_permission(self.role_1, self.permission)
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_2, self.user, "view_perm")
        self.assertEqual(result, True)

        # Remove individual permission
        result = merengue.perms.utils.remove_permission(self.role_1, self.permission, self.page_1)
        self.assertEqual(result, True)

        # Try individual permission
        result = merengue.perms.utils.remove_permission(self.role_1, self.permission, self.page_2)
        self.assertEqual(result, False)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_2, self.user, "view_perm")
        self.assertEqual(result, True)

        # Remove global permission
        result = merengue.perms.utils.remove_permission(self.role_1, self.permission)
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, False)

        result = merengue.perms.utils.has_permission(self.page_2, self.user, "view_perm")
        self.assertEqual(result, False)

        # Add global permission
        result = merengue.perms.utils.grant_permission(self.role_1, self.permission)
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, True)

        # Non inherited permissions
        self.page_1.adquire_global_permissions = False
        self.page_1.save()
        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, False)

        # Add individual permission
        result = merengue.perms.utils.grant_permission(self.role_1, self.permission, self.page_1)
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_2, self.user, "view_perm")
        self.assertEqual(result, True)

        # Remove individual permission
        result = merengue.perms.utils.remove_permission(self.role_1, self.permission, self.page_1)
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, False)

        # Inherited permissions
        self.page_1.adquire_global_permissions = True
        self.page_1.save()
        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, True)

        # Remove global permission
        result = merengue.perms.utils.remove_permission(self.role_1, self.permission)
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, False)

    def test_has_permission_owner(self):
        """
        """
        creator = User.objects.create(username="jane")

        result = merengue.perms.utils.has_permission(self.page_1, creator, "view_perm")
        self.assertEqual(result, False)

        owner = Role.objects.get(name="Owner")
        merengue.perms.utils.grant_permission(owner, "view_perm", self.page_1)

        result = merengue.perms.utils.has_permission(self.page_1, creator, "view_perm", [owner])
        self.assertEqual(result, True)

    def test_local_role(self):
        """
        """
        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, False)

        merengue.perms.utils.grant_permission(self.role_2, self.permission, self.page_1)
        merengue.perms.utils.add_local_role(self.page_1, self.user, self.role_2)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, True)

    def test_ineritance(self):
        """
        """
        result = merengue.perms.utils.is_inherited(self.page_1, "view_perm")
        self.assertEqual(result, True)

        # per permission
        merengue.perms.utils.add_inheritance_block(self.page_1, self.permission)

        result = merengue.perms.utils.is_inherited(self.page_1, "view_perm")
        self.assertEqual(result, False)

        merengue.perms.utils.remove_inheritance_block(self.page_1, self.permission)

        result = merengue.perms.utils.is_inherited(self.page_1, "view_perm")
        self.assertEqual(result, True)

        # per codename
        merengue.perms.utils.add_inheritance_block(self.page_1, "view_perm")

        result = merengue.perms.utils.is_inherited(self.page_1, "view_perm")
        self.assertEqual(result, False)

        merengue.perms.utils.remove_inheritance_block(self.page_1, "view_perm")

        result = merengue.perms.utils.is_inherited(self.page_1, "view_perm")
        self.assertEqual(result, True)

    def test_unicode(self):
        """
        """
        # Permission
        self.assertEqual(self.permission.__unicode__(), "View permission (view_perm)")

        # ObjectPermission
        merengue.perms.utils.grant_permission(self.role_1, self.permission, self.page_1)
        opr = ObjectPermission.objects.get(permission=self.permission, role=self.role_1)
        self.assertEqual(opr.__unicode__(), "View permission / Role 1 / Page 1")

        # ObjectPermissionInheritanceBlock
        merengue.perms.utils.add_inheritance_block(self.page_1, self.permission)
        opb = ObjectPermissionInheritanceBlock.objects.get(permission=self.permission)

        self.assertEqual(opb.__unicode__(), "View permission (view_perm) / Page 1")

    def test_reset(self):
        """
        """
        result = merengue.perms.utils.grant_permission(self.role_1, "view_perm", self.page_1)
        self.assertEqual(result, True)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, True)

        merengue.perms.utils.add_inheritance_block(self.page_1, "view_perm")

        result = merengue.perms.utils.is_inherited(self.page_1, "view_perm")
        self.assertEqual(result, False)

        merengue.perms.utils.reset(self.page_1)

        result = merengue.perms.utils.has_permission(self.page_1, self.user, "view_perm")
        self.assertEqual(result, False)

        result = merengue.perms.utils.is_inherited(self.page_1, "view_perm")
        self.assertEqual(result, True)

        merengue.perms.utils.reset(self.page_1)


class RegistrationTestCase(TestCase):
    """Tests the registration of different components.
    """

    def test_group(self):
        """Tests registering/unregistering of a group.
        """
        # Register a group
        result = merengue.perms.utils.register_group("Brights")
        self.failUnless(isinstance(result, Group))

        # It's there
        group = Group.objects.get(name="Brights")
        self.assertEqual(group.name, "Brights")

        # Trying to register another group with same name
        result = merengue.perms.utils.register_group("Brights")
        self.assertEqual(result, False)

        group = Group.objects.get(name="Brights")
        self.assertEqual(group.name, "Brights")

        # Unregister the group
        result = merengue.perms.utils.unregister_group("Brights")
        self.assertEqual(result, True)

        # It's not there anymore
        self.assertRaises(Group.DoesNotExist, Group.objects.get, name="Brights")

        # Trying to unregister the group again
        result = merengue.perms.utils.unregister_group("Brights")
        self.assertEqual(result, False)

    def test_role(self):
        """Tests registering/unregistering of a role.
        """
        # Register a role
        result = merengue.perms.utils.register_role("Editor")
        self.failUnless(isinstance(result, Role))

        # It's there
        role = Role.objects.get(name="Editor")
        self.assertEqual(role.name, "Editor")

        # Trying to register another role with same name
        result = merengue.perms.utils.register_role("Editor")
        self.assertEqual(result, False)

        role = Role.objects.get(name="Editor")
        self.assertEqual(role.name, "Editor")

        # Unregister the role
        result = merengue.perms.utils.unregister_role("Editor")
        self.assertEqual(result, True)

        # It's not there anymore
        self.assertRaises(Role.DoesNotExist, Role.objects.get, name="Editor")

        # Trying to unregister the role again
        result = merengue.perms.utils.unregister_role("Editor")
        self.assertEqual(result, False)

    def test_permission(self):
        """Tests registering/unregistering of a permission.
        """
        # Register a permission
        result = merengue.perms.utils.register_permission("Change", "change")
        self.failUnless(isinstance(result, Permission))

        # Is it there?
        p = Permission.objects.get(codename="change")
        self.assertEqual(p.name, "Change")

        # Register a permission with the same codename
        result = merengue.perms.utils.register_permission("Change2", "change")
        self.assertEqual(result, False)

        # Is it there?
        p = Permission.objects.get(codename="change")
        self.assertEqual(p.name, "Change")

        # Register a permission with the same name
        result = merengue.perms.utils.register_permission("Change", "change2")
        self.assertEqual(result, False)

        # Is it there?
        p = Permission.objects.get(codename="change")
        self.assertEqual(p.name, "Change")

        # Unregister the permission
        result = merengue.perms.utils.unregister_permission("change")
        self.assertEqual(result, True)

        # Is it not there anymore?
        self.assertRaises(Permission.DoesNotExist, Permission.objects.get, codename="change")

        # Unregister the permission again
        result = merengue.perms.utils.unregister_permission("change")
        self.assertEqual(result, False)

        # Register a permission with content types
        ctypes = [ContentType.objects.get_for_model(BaseContent)]
        perm_1 = merengue.perms.utils.register_permission(
            "Change BaseContent", "change_basecontent", ctypes=ctypes,
        )
        self.assertEqual(list(perm_1.content_types.all()), ctypes)
        perm_2 = merengue.perms.utils.register_permission(
            "View BaseContent", "view_basecontent", for_models=[BaseContent])
        self.assertEqual(list(perm_2.content_types.all()), ctypes)


# django imports
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.sessions.backends.file import SessionStore


# Taken from "http://www.djangosnippets.org/snippets/963/"


class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function,
    just as if that view had been hooked up using a URLconf.

    """

    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)


def create_request():
    """
    """
    rf = RequestFactory()
    request = rf.get('/')
    request.session = SessionStore()

    user = User()
    user.is_superuser = True
    user.save()
    request.user = user

    return request
