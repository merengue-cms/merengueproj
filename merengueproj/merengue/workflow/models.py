# Copyright (c) 2010 by Yaco Sistemas <precio@yaco.es>
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
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from merengue.perms.models import Permission, Role
from merengue.perms.utils import has_permission


class Workflow(models.Model):
    """A workflow consists of a sequence of connected (through transitions)
    states. It can be assigned to a model and / or model instances. If a
    model instance has a workflow it takes precendence over the model's
    workflow.

    **Attributes:**

    model
        The model the workflow belongs to. Can be any

    content
        The object the workflow belongs to.

    name
        The unique name of the workflow.

    states
        The states of the workflow.

    initial_state
        The initial state the model / content gets if created.
    """

    name = models.CharField(_("Name"), max_length=100, unique=True)
    initial_state = models.ForeignKey("State", related_name="workflow_state",
                                      blank=True, null=True)
    permissions = models.ManyToManyField(Permission, symmetrical=False,
                                         through="WorkflowPermissionRelation")

    def __unicode__(self):
        return self.name

    def get_initial_state(self):
        """Returns the initial state of the workflow. Takes the first one if
        no state has been defined.
        """
        if self.initial_state:
            return self.initial_state
        else:
            try:
                return self.states.all()[0]
            except IndexError:
                return None

    def set_to_model(self, ctype):
        """Sets the workflow to the passed content type. If the content
        type has already an assigned workflow the workflow is overwritten.

        **Parameters:**

        ctype
            The content type which gets the workflow. Can be any Django model
            instance.
        """
        try:
            wor = WorkflowModelRelation.objects.get(content_type=ctype)
        except WorkflowModelRelation.DoesNotExist:
            WorkflowModelRelation.objects.create(content_type=ctype,
                                                 workflow=self)
        else:
            wor.workflow = self
            wor.save()

    def add_permission(self, perm):
        """Add a permission that will be used on this workflow
        """
        WorkflowPermissionRelation.objects.create(workflow=self,
                                                  permission=perm)


class State(models.Model):
    """A certain state within workflow.

    **Attributes:**

    name
        The unique name of the state within the workflow.

    workflow
        The workflow to which the state belongs.

    transitions
        The transitions of a workflow state.
    """
    name = models.CharField(_(u"Name"), max_length=100)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"),
                                 related_name="states")
    transitions = models.ManyToManyField("Transition",
                                         verbose_name=_(u"Transitions"),
                                         blank=True, null=True,
                                         related_name="states")

    class Meta:
        ordering = ('name', )

    def delete(self, *args, **kwargs):
        if self.workflow_state.count():
            self.workflow_state.clear()
        super(State, self).delete(*args, **kwargs)

    def get_allowed_transitions(self, obj, user):
        """Returns all allowed transitions for passed object and user.
        """
        transitions = []
        for transition in self.transitions.all():
            permission = transition.permission
            if permission is None:
                transitions.append(transition)
            else:
                # First we try to get the objects specific has_permission
                # method (in case the object inherits from the PermissionBase
                # class).
                try:
                    if obj.has_permission(user, permission.codename):
                        transitions.append(transition)
                except AttributeError:
                    if has_permission(obj, user,
                                      permission.codename):
                        transitions.append(transition)
        return transitions

    def get_accesible_states(self):
        """
        This function return a list with all accesible states from
        the own state.
        """
        states = [transition.destination
                  for transition
                  in self.transitions.all()]

        return list(set(states))

    def get_permissions_by_role(self, role):
        """
        """
        return [stateperm.permission for stateperm
                in StatePermissionRelation.objects.filter(
                    state=self, role=role)]

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.workflow.name)


class Transition(models.Model):
    """A transition from a source to a destination state. The transition can
    be used from several source states.

    **Attributes:**

    name
        The unique name of the transition within a workflow.

    workflow
        The workflow to which the transition belongs. Must be a Workflow
        instance.

    destination
        The state after a transition has been processed. Must be a State
        instance.

    permission
        The necessary permission to process the transition. Must be a
        Permission instance.
    """
    name = models.CharField(_(u"Name"), max_length=100)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"),
                                 related_name="transitions")
    destination = models.ForeignKey(State, verbose_name=_(u"Destination"),
                                    null=True, blank=True,
                                    related_name="destination_state")
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"),
                                   blank=True, null=True)

    def __unicode__(self):
        return self.name


class WorkflowModelRelation(models.Model):
    """Stores an workflow for a model (ContentType).

    Provides a way to give any object a workflow without changing the model.

    **Attributes:**

    Content Type
        The content type for which the workflow is stored. This can be any
        instance of a Django model.

    workflow
        The workflow which is assigned to an object. This needs to be a
        workflow instance.
    """
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_(u"Content Type"),
                                     unique=True)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"),
                                 related_name="wmrs")

    def __unicode__(self):
        return "%s - %s" % (self.content_type.name, self.workflow.name)


# Permissions relation


class WorkflowPermissionRelation(models.Model):
    """Stores the permissions for which a workflow is responsible.

    **Attributes:**

    workflow
        The workflow which is responsible for the permissions. Needs to be a
        Workflow instance.

    permission
        The permission for which the workflow is responsible. Needs to be a
        Permission instance.
    """
    workflow = models.ForeignKey(Workflow)
    permission = models.ForeignKey(Permission, related_name="permissions")

    class Meta:
        unique_together = ("workflow", "permission")

    def __unicode__(self):
        return "%s %s" % (self.workflow.name, self.permission.name)


class StateInheritanceBlock(models.Model):
    """Stores inheritance block for state and permission.

    **Attributes:**

    state
        The state for which the inheritance is blocked. Needs to be a State
        instance.

    permission
        The permission for which the instance is blocked. Needs to be a
        Permission instance.
    """
    state = models.ForeignKey(State, verbose_name=_(u"State"))
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"))

    def __unicode__(self):
        return "%s %s" % (self.state.name, self.permission.name)


class StatePermissionRelation(models.Model):
    """Stores granted permission for state and role.

    **Attributes:**

    state
        The state for which the role has the permission. Needs to be a State
        instance.

    permission
        The permission for which the workflow is responsible. Needs to be a
        Permission instance.

    role
        The role for which the state has the permission. Needs to be a lfc
        Role instance.
    """
    state = models.ForeignKey(State, verbose_name=_(u"State"))
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"))
    role = models.ForeignKey(Role, verbose_name=_(u"Role"))

    def __unicode__(self):
        return "%s %s %s" % (self.state.name, self.role.name,
                             self.permission.name)
