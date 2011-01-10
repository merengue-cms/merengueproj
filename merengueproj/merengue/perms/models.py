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

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent


class Permission(models.Model):
    """A permission which can be granted to users/groups and objects.

    **Attributes:**

    name
        The unique name of the permission. This is displayed to users.

    codename
        The unique codename of the permission. This is used internal to
        identify a permission.

    builtin
        A builtin permission will appears in the manage permission view of
        every content. Will be False by default.

    content_types
        The content types for which the permission is active. This can be
        used to display only reasonable permissions for an object.
    """
    name = models.CharField(_(u"Name"), max_length=100, unique=True)
    codename = models.CharField(_(u"Codename"), max_length=100, unique=True)
    builtin = models.BooleanField(_(u"Builtin permission"), default=False, editable=False)
    content_types = models.ManyToManyField(ContentType, verbose_name=_(u"Content Types"), blank=True, null=True, related_name="content_types")

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.codename)


class ObjectPermission(models.Model):
    """Grants permission for specific user/group and object.

    **Attributes:**

    role
        The role for which the permission is granted.

    permission
        The permission which is granted.

    content
        The object for which the permission is granted.
    """
    role = models.ForeignKey("Role", verbose_name=_(u"Role"), blank=True, null=True)
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"))

    content = models.ForeignKey(BaseContent, blank=True, null=True)

    def __unicode__(self):
        return u"%s / %s / %s" % (self.permission.name, self.role, self.content)

    def get_principal(self):
        """Returns the principal.
        """
        return self.user or self.group

    def set_principal(self, principal):
        """Sets the principal.
        """
        if isinstance(principal, User):
            self.user = principal
        else:
            self.group = principal

    principal = property(get_principal, set_principal)


class ObjectPermissionInheritanceBlock(models.Model):
    """Blocks the inheritance for specific permission and object.

    **Attributes:**

    permission
        The permission for which inheritance is blocked.

    content
        The object for which the inheritance is blocked.
    """
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"))
    content = models.ForeignKey(BaseContent)

    def __unicode__(self):
        return u"%s / %s" % (self.permission, self.content)


class Role(models.Model):
    """A role gets permissions to do something. Principals (users and groups)
    can only get permissions via roles.

    **Attributes:**

    name
        The unique name of the role
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(verbose_name=_('slug'), max_length=200,
                            db_index=True, unique=True)

    class Meta:
        ordering = ("name", )

    def __unicode__(self):
        return self.name

    def add_principal(self, principal, content=None):
        """
        """
        if isinstance(principal, User):
            PrincipalRoleRelation.objects.create(user=principal, role=self)
        else:
            PrincipalRoleRelation.objects.create(group=principal, role=self)

    def get_groups(self, content=None):
        """Returns all groups which has this role assigned.
        """
        return PrincipalRoleRelation.objects.filter(role=self, content=content)

    def get_users(self, content=None):
        """Returns all users which has this role assigned.
        """
        return PrincipalRoleRelation.objects.filter(role=self, content=content)


class PrincipalRoleRelation(models.Model):
    """A role given to a principal (user or group). If a content object is
    given this is a local role, i.e. the principal has this role only for this
    content object. Otherwise it is a global role, i.e. the principal has
    this role generally.

    user
        A user instance. Either a user xor a group needs to be given.

    group
        A group instance. Either a user xor a group needs to be given.

    role
        The role which is given to the principal for content.

    content
        The content object which gets the local role (optional).
    """
    user = models.ForeignKey(User, verbose_name=_(u"User"), blank=True, null=True)
    group = models.ForeignKey(Group, verbose_name=_(u"Group"), blank=True, null=True)
    role = models.ForeignKey(Role, verbose_name=_(u"Role"))
    content = models.ForeignKey(BaseContent, blank=True, null=True)

    def get_principal(self):
        """Returns the principal.
        """
        return self.user or self.group

    def set_principal(self, principal):
        """Sets the principal.
        """
        if isinstance(principal, User):
            self.user = principal
        else:
            self.group = principal

    principal = property(get_principal, set_principal)

    def __unicode__(self):
        if self.content:
            return u"%s / %s / %s" % (self.user or self.group, self.role, self.content)
        else:
            return u"%s / %s" % (self.user or self.group, self.role)
