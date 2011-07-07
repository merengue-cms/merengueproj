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
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext, get_language, activate, ugettext_lazy as _

from south.signals import post_migrate
from transmeta import (TransMeta, get_fallback_fieldname, get_real_fieldname,
                       get_real_fieldname_in_each_language, fallback_language)

from merengue import perms  # pyflakes:ignore
from merengue.workflow.managers import WorkflowManager


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

    __metaclass__ = TransMeta
    name = models.CharField(_("Name"), max_length=100)
    slug = models.CharField(_(u"Slug"), max_length=100)
    initial_state = models.ForeignKey("State", related_name="workflow_state",
                                      blank=True, null=True, on_delete=models.SET_NULL)
    permissions = models.ManyToManyField('perms.Permission',
                                         symmetrical=False,
                                         through="WorkflowPermissionRelation")

    objects = WorkflowManager()

    class Meta:
        verbose_name = _('Workflow')
        verbose_name_plural = _('Workflows')
        translate = ('name', )

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

    def blank(self):
        """ Removes all the transitions, permissions, and states """
        self.states.all().delete()
        self.initial_state.delete()
        self.transitions.all().delete()
        self.permissions.clear()

    def is_empty(self):
        return not self.states.all().exists() and not self.transitions.all().exists()


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
    __metaclass__ = TransMeta
    name = models.CharField(_(u"Name"), max_length=100)
    slug = models.CharField(_(u"Slug"), max_length=100)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"),
                                 related_name="states")
    transitions = models.ManyToManyField("Transition",
                                         verbose_name=_(u"Transitions"),
                                         blank=True, null=True,
                                         related_name="states")

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')
        translate = ('name', )
        ordering = (get_fallback_fieldname('name'), )

    def __unicode__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.workflow_state.count():
            self.workflow_state.clear()
        super(State, self).delete(*args, **kwargs)

    def get_allowed_transitions(self, user, obj):
        """Returns all allowed transitions for passed object and user.
        """
        from merengue.perms.utils import has_permission
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

    def get_accesible_states(self, user, obj):
        transitions = self.get_allowed_transitions(user, obj)
        states_pk = [transition.destination.pk
                     for transition
                     in transitions] + [self.pk]
        return State.objects.filter(pk__in=states_pk)

    def get_all_states(self):
        """
        This function return a list with all accesible states from
        the own state.
        """
        states_pk = [transition.destination.pk
                     for transition
                     in self.transitions.all()] + [self.pk]

        return State.objects.filter(pk__in=states_pk)

    def get_permissions_by_role(self, role):
        """
        """
        return [stateperm.permission for stateperm
                in StatePermissionRelation.objects.filter(
                    state=self, role=role)]

    def set_permissions(self, permission_dict):
        """
        Set the permission in the state passing a dict like this:

        {'owner': ('view', 'edit', ),
         'reviewer': ('view', 'edit', 'delete'),}
        """
        for role_slug, permission_codenames in permission_dict.items():
            role = perms.models.Role.objects.get(slug=role_slug)
            for codename in permission_codenames:
                permission = perms.models.Permission.objects.get(codename=codename)
                StatePermissionRelation.objects.get_or_create(
                    state=self,
                    permission=permission,
                    role=role,
                )


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
    __metaclass__ = TransMeta
    name = models.CharField(_(u"Name"), max_length=100)
    slug = models.CharField(_(u"Slug"), max_length=100)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"),
                                 related_name="transitions")
    destination = models.ForeignKey(State, verbose_name=_(u"Destination"),
                                    null=True, blank=True,
                                    related_name="destination_state")
    permission = models.ForeignKey('perms.Permission',
                                   verbose_name=_(u"Permission"),
                                   blank=True, null=True)

    class Meta:
        verbose_name = _('Transition')
        verbose_name_plural = _('Transitions')
        translate = ('name', )

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

    def natural_key(self):
        return (self.workflow.slug,) + self.content_type.natural_key()
    natural_key.dependencies = ['contenttypes.contenttype']

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
    permission = models.ForeignKey('perms.Permission', related_name="permissions")

    class Meta:
        unique_together = ("workflow", "permission")

    def natural_key(self):
        return (self.workflow.slug, self.permission.codename)

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
    permission = models.ForeignKey('perms.Permission', verbose_name=_(u"Permission"))

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
    permission = models.ForeignKey('perms.Permission', verbose_name=_(u"Permission"))
    role = models.ForeignKey('perms.Role', verbose_name=_(u"Role"), blank=True, null=True)

    def natural_key(self):
        return (self.role.slug, self.permission.codename,
                self.state.slug, self.state.workflow.slug)

    def __unicode__(self):
        return "%s %s %s" % (self.state.name, self.role.name,
                             self.permission.name)


def populate_workflow(workflow):
    """
    Populate the workflow with states, transitions and permissions
    """
    from merengue.perms.models import Role, Permission

    name_fields = get_real_fieldname_in_each_language('name')
    old_lang = get_language()
    activate(fallback_language())
    for field in name_fields:
        value = getattr(workflow, field, True)
        if value == '':
            setattr(workflow, field, None)
    data = {get_real_fieldname('name'): ugettext('Draft')}
    draft = State.objects.create(slug='draft', workflow=workflow, **data)
    draft.set_permissions({
        perms.ANONYMOUS_ROLE_SLUG: ('view', ),
        perms.OWNER_ROLE_SLUG: ('edit', 'delete', 'can_draft', 'can_pending', ),
        perms.REVIEWER_ROLE_SLUG: ('edit', 'delete', 'can_draft', 'can_pending', 'can_published'),
    })

    data = {get_real_fieldname('name'): ugettext('Pending')}
    pending = State.objects.create(slug='pending', workflow=workflow, **data)
    pending.set_permissions({
        perms.ANONYMOUS_ROLE_SLUG: ('view', ),
        perms.OWNER_ROLE_SLUG: ('edit', 'delete', 'can_draft', 'can_pending', ),
        perms.REVIEWER_ROLE_SLUG: ('edit', 'delete', 'can_draft', 'can_pending', 'can_published'),
    })

    data = {get_real_fieldname('name'): ugettext('Published')}
    published = State.objects.create(slug='published', workflow=workflow, **data)
    published.set_permissions({
        perms.ANONYMOUS_ROLE_SLUG: ('view', ),
        perms.OWNER_ROLE_SLUG: (),
        perms.REVIEWER_ROLE_SLUG: ('edit', 'delete', 'can_draft', 'can_pending', 'can_published'),
    })

    data = {get_real_fieldname('name'): ugettext('Set as pending')}
    pending_permission = Permission.objects.get(codename='can_pending')
    set_as_pending = Transition.objects.create(
        slug='set-as-pending', workflow=workflow, destination=pending,
        permission=pending_permission, **data)

    data = {get_real_fieldname('name'): ugettext('Set as draft')}
    draft_permission = Permission.objects.get(codename='can_draft')
    set_as_draft = Transition.objects.create(
        slug='set-as-draft', workflow=workflow, destination=draft,
        permission=draft_permission, **data)

    data = {get_real_fieldname('name'): ugettext('Publish')}
    publish_permission = Permission.objects.get(codename='can_published')
    publish = Transition.objects.create(
        slug='publish', workflow=workflow, destination=published,
        permission=publish_permission, **data)

    draft.transitions.add(set_as_pending)
    draft.transitions.add(publish)
    pending.transitions.add(publish)
    pending.transitions.add(set_as_draft)
    published.transitions.add(set_as_pending)
    published.transitions.add(set_as_draft)
    try:
        anonymous_role = Role.objects.get(slug=perms.ANONYMOUS_ROLE_SLUG)
    except Role.DoesNotExist:
        # maybe the role does not exist (for example when tests are running)
        anonymous_role = Role.objects.create(id=1, slug=perms.ANONYMOUS_ROLE_SLUG)
    try:
        view_permission = Permission.objects.get(codename='view')
    except Permission.DoesNotExist:
        # maybe the permission does not exist (for example when tests are running)
        view_permission = Permission.objects.create(id=1, codename='view')

    StatePermissionRelation.objects.create(
        state=published, permission=view_permission, role=anonymous_role,
        )
    for codename in ('view', 'edit', 'delete', 'can_draft', 'can_pending',
                     'can_published', 'manage_category', 'manage_link',
                     'manage_menu', 'manage_block', ):
        WorkflowPermissionRelation.objects.create(
            permission=Permission.objects.get(codename=codename),
            workflow=workflow,
        )
    workflow.initial_state = draft
    workflow.save()
    activate(old_lang)


def create_default_states_handler(sender, instance, **kwargs):
    created = kwargs.pop('created', False)
    if created and instance.is_empty():
        populate_workflow(instance)


def populate_initial_workflow_handler(sender, **kwargs):
    app = kwargs['app']
    if app == 'workflow':
        try:
            workflow = Workflow.objects.default_workflow()
            if not workflow.states.all().exists():  # never has been populated
                populate_workflow(workflow)
        except Workflow.DoesNotExist:
            pass  # maybe has been deleted
    elif app == 'base':
        from merengue.base.models import BaseContent
        try:
            workflow = Workflow.objects.default_workflow()
            if not WorkflowModelRelation.objects.filter(workflow=workflow).exists():
                content_type = ContentType.objects.get_for_model(BaseContent)
                WorkflowModelRelation.objects.create(
                    content_type=content_type,
                    workflow=workflow,
                )
        except Workflow.DoesNotExist:
            pass  # maybe has been deleted

post_migrate.connect(populate_initial_workflow_handler)
post_save.connect(create_default_states_handler, sender=Workflow)
