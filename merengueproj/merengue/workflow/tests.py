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

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from merengue.perms.models import Permission, Role
from merengue.workflow.models import (Workflow, State, Transition,
                                      WorkflowModelRelation,
                                      WorkflowPermissionRelation,
                                      StatePermissionRelation)


class WorkflowBaseTestCase(TestCase):

    def setUp(self):
        Workflow.objects.all().delete()


class WorkflowBasicTest(WorkflowBaseTestCase):
    """This TestCase will test the most simplest aspect
    of Workflow model.
    """

    def test_basic_creation(self):
        """Test the creation of a empty Workflow object.
        """
        self.assertEquals(Workflow.objects.count(), 0)
        Workflow.objects.create(name_en='Foo Workflow', slug='foo-workflow')
        Workflow.objects.create(name_en='Bar Workflow', slug='bar-workflow')
        self.assertEquals(Workflow.objects.count(), 2)
        self.assertEquals(State.objects.count(), 6)  # post_save creates 3 states per workflow
        self.assertEquals(Transition.objects.count(), 6)  # post_save creates 3 transitions per workflow

        work = Workflow.objects.get(slug='foo-workflow')
        self.assertTrue(work.permissions.count() > 0)
        self.assertEquals(work.states.count(), 3)
        self.assertEquals(work.transitions.count(), 3)
        self.assertEquals(work.initial_state, State.objects.get(
                workflow=work, slug='draft'))

    def test_workflow_permission_relation(self):
        """Test the relationship between a Workflow and the permissions
        associated with them.
        """
        work = Workflow.objects.create(
            name_en='Foo Workflow', slug='foo-workflow')
        work.blank()

        permissions = []
        permissions.append(Permission.objects.get(codename=u'can_draft'))
        permissions.append(Permission.objects.get(codename=u'can_pending'))
        permissions.append(Permission.objects.get(codename=u'can_published'))
        permissions.append(Permission.objects.get(codename=u'delete'))
        permissions.append(Permission.objects.get(codename=u'edit'))
        permissions.append(Permission.objects.get(codename=u'view'))

        for perm in permissions:
            work.add_permission(perm)

        self.assertEquals(Workflow.objects.count(), 1)
        self.assertEquals(work.permissions.count(), 6)
        self.assertEquals(work.permissions.all()[0].name,
                          u'Can set as draft')
        self.assertEquals(work.permissions.all()[3].builtin, True)
        self.assertEquals(work.permissions.all()[3].name,
                          u'Delete')

    def test_content_type_association(self):
        """Test the assosiaction of a ContentType with a Workflow
        """

        # Create a Workflow and get ContentType like Document
        self.assertEquals(WorkflowModelRelation.objects.count(), 0)
        work = Workflow.objects.create(
            name_en='Foo Workflow', slug='foo-workflow')
        doc = ContentType.objects.get(name='document', app_label='section')

        # Set the workflow to the model
        self.assertEquals(WorkflowModelRelation.objects.count(), 0)
        work.set_to_model(doc)
        self.assertEquals(WorkflowModelRelation.objects.count(), 1)
        relation_1 = WorkflowModelRelation.objects.all()[0]
        self.assertEquals(relation_1.content_type_id, doc.id)
        self.assertEquals(relation_1.workflow_id, work.id)

        # Set the same workflow to other model
        video = ContentType.objects.get(name='video')
        work.set_to_model(video)
        self.assertEquals(WorkflowModelRelation.objects.count(), 2)
        relation_2 = WorkflowModelRelation.objects.all()[1]
        self.assertEquals(relation_2.content_type_id, video.id)
        self.assertEquals(relation_2.workflow_id, work.id)

        # Create a new workflow and change the workflow associated to video CT
        new_work = Workflow.objects.create(
            name_en='Bar Workflow', slug='bar-workflow')
        new_work.set_to_model(video)
        self.assertEquals(WorkflowModelRelation.objects.count(), 2)
        relation_2 = WorkflowModelRelation.objects.all()[1]
        self.assertEquals(relation_2.content_type_id, video.id)
        self.assertEquals(relation_2.workflow_id, new_work.id)

    def test_workflow_creation_and_delete(self):
        work = Workflow.objects.create(name_en='foo workflow')
        work.blank()

        permissions = []
        permissions.append(Permission.objects.get(codename=u'can_draft'))
        permissions.append(Permission.objects.get(codename=u'can_pending'))
        permissions.append(Permission.objects.get(codename=u'can_published'))
        permissions.append(Permission.objects.get(codename=u'delete'))
        permissions.append(Permission.objects.get(codename=u'edit'))
        permissions.append(Permission.objects.get(codename=u'view'))

        for perm in permissions:
            work.add_permission(perm)

        work.set_to_model(ContentType.objects.get(name='document', app_label='section'))

        self.assertEquals(work.permissions.count(), 6)
        self.assertEquals(WorkflowPermissionRelation.objects.count(), 6)
        self.assertEquals(WorkflowModelRelation.objects.count(), 1)
        work.delete()
        self.assertEquals(WorkflowPermissionRelation.objects.count(), 0)
        self.assertEquals(WorkflowModelRelation.objects.count(), 0)

    def tearDown(self):
        pass


class WorkflowStatesBasicTest(WorkflowBaseTestCase):
    """Tests about the relation between Workflow and State objects.
    """

    def setUp(self):
        """With this setting up, we instance a basic Workflow
        with some perms that will be manage by it, and a ContentType
        that will use that Workflow
        """
        super(WorkflowStatesBasicTest, self).setUp()
        self.work = Workflow.objects.create(
            name_en='Foo Workflow', slug='foo-workflow')

        self.work.initial_state = None
        [state.delete() for state in self.work.states.all()]

        permissions = []
        permissions.append(Permission.objects.get(codename=u'can_draft'))
        permissions.append(Permission.objects.get(codename=u'can_pending'))
        permissions.append(Permission.objects.get(codename=u'can_published'))
        permissions.append(Permission.objects.get(codename=u'delete'))
        permissions.append(Permission.objects.get(codename=u'edit'))
        permissions.append(Permission.objects.get(codename=u'view'))

        for perm in permissions:
            self.work.add_permission(perm)

        self.work.set_to_model(ContentType.objects.get(name='document', app_label='section'))

    def test_basic_states_creation(self):
        """Test the creation of some states for the Workflow
        """
        self.assertEquals(State.objects.count(), 0)
        State.objects.create(name_en="Draft", slug='draft', workflow=self.work)
        State.objects.create(name_en="Reviewed", slug='reviewed', workflow=self.work)
        State.objects.create(name_en="Rejected", slug='rejected', workflow=self.work)
        State.objects.create(name_en="Published", slug='published', workflow=self.work)
        State.objects.create(name_en="On top", slug='on-top', workflow=self.work)

        self.assertEquals(State.objects.count(), self.work.states.count())

        gen_states_name = [state.name for state in State.objects.all()]
        work_states_name = [state.name for state in self.work.states.all()]

        gen_states_name.sort()
        work_states_name.sort()
        self.assertEquals(gen_states_name, work_states_name)

    def test_set_initial_state(self):
        """Test to check the proper setting of a initial state for the workflow
        """
        State.objects.create(name_en="Draft", slug='draft', workflow=self.work)
        State.objects.create(name_en="Reviewed", slug='reviewed', workflow=self.work)
        State.objects.create(name_en="Rejected", slug='rejected', workflow=self.work)
        State.objects.create(name_en="Published", slug='published', workflow=self.work)
        State.objects.create(name_en="On top", slug='on-top', workflow=self.work)

        self.assertEquals(self.work.get_initial_state(),
                          self.work.states.all()[0])

        self.work.initial_state = State.objects.get(slug="published")
        self.assertEquals(self.work.get_initial_state(),
                          self.work.states.get(slug="published"))

    def test_get_initial_state_from_content_type(self):
        """Test if it's possible to get the initial state of a workflow
        accessing through ContentType
        """
        State.objects.create(name_en="Draft", slug='draft', workflow=self.work)
        State.objects.create(name_en="Reviewed", slug='reviewed', workflow=self.work)
        State.objects.create(name_en="Rejected", slug='rejected', workflow=self.work)
        State.objects.create(name_en="Published", slug='published', workflow=self.work)
        State.objects.create(name_en="On top", slug='on-top', workflow=self.work)

        self.work.initial_state = State.objects.get(slug="draft")
        self.work.save()

        doc = ContentType.objects.get(name='document', app_label='section')
        obtained_workflow = WorkflowModelRelation.objects.get(
            content_type=doc).workflow

        self.assertEquals(self.work.initial_state,
                          obtained_workflow.get_initial_state())

    def test_removing_initial_state(self):
        """Test that the workflow behaviour is correct after removing the
        initial state.
        """
        State.objects.create(name_en="Draft", slug='draft', workflow=self.work)
        State.objects.create(name_en="Reviewed", slug='reviewed', workflow=self.work)
        State.objects.create(name_en="Rejected", slug='rejected', workflow=self.work)
        State.objects.create(name_en="Published", slug='published', workflow=self.work)
        State.objects.create(name_en="On top", slug='on-top', workflow=self.work)

        self.work.initial_state = State.objects.get(slug="draft")
        self.work.save()

        self.assertEquals(self.work.get_initial_state(),
                          self.work.states.all()[0])
        self.assertEquals(self.work.get_initial_state().name_en, "Draft")
        State.objects.get(slug="draft").delete()

        # As we changed a lot of the Workflow structure, we need to
        # load it again from database
        self.work = Workflow.objects.all()[0]
        self.assertEquals(self.work.get_initial_state(),
                          self.work.states.all()[0])
        self.assertEquals(self.work.get_initial_state().name_en, "On top")

    def test_removing_all_states(self):
        """Test that the workflow behaviour is correct after removing
        all the states.
        """
        State.objects.create(name_en="Draft", slug='draft', workflow=self.work)
        State.objects.create(name_en="Reviewed", slug='reviewed', workflow=self.work)
        State.objects.create(name_en="Rejected", slug='rejected', workflow=self.work)
        State.objects.create(name_en="Published", slug='published', workflow=self.work)
        State.objects.create(name_en="On top", slug='on-top', workflow=self.work)

        self.assertEquals(self.work.states.count(), 5)
        some_state = State.objects.all()[2]
        some_state.delete()
        self.assertEquals(self.work.states.count(), 4)

        State.objects.create(name_en="Modified", slug='modified', workflow=self.work)
        self.assertEquals(self.work.states.count(), 5)

        self.work.states.all().delete()
        self.assertEquals(self.work.states.count(), 0)
        self.assertEquals(self.work.get_initial_state(), None)

    def tearDown(self):
        self.work.delete()


class WorkflowTransitionBasicTest(WorkflowBaseTestCase):
    """This TestCase will test the relations with Transitions
    objects, basically between State and Transittion.
    """

    def setUp(self):
        """With this setting up, we instance a basic Workflow
        with some perms that will be manage by it, and a ContentType
        that will use that Workflow.

        It also adds the States objects
        """
        super(WorkflowTransitionBasicTest, self).setUp()
        self.work = Workflow.objects.create(
            name_en='Foo Workflow', slug='foo-workflow')
        # after save the workflow is populated. We want a blank workflow
        self.work.blank()

        self.work.initial_state = None
        [state.delete() for state in self.work.states.all()]
        [transition.delete() for transition in self.work.transitions.all()]

        permissions = []
        permissions.append(Permission.objects.get(codename=u'can_draft'))
        permissions.append(Permission.objects.get(codename=u'can_pending'))
        permissions.append(Permission.objects.get(codename=u'can_published'))
        permissions.append(Permission.objects.get(codename=u'delete'))
        permissions.append(Permission.objects.get(codename=u'edit'))
        permissions.append(Permission.objects.get(codename=u'view'))

        for perm in permissions:
            self.work.add_permission(perm)

        self.work.set_to_model(ContentType.objects.get(name='document', app_label='section'))

        State.objects.create(name_en="Draft", slug='draft', workflow=self.work)
        State.objects.create(name_en="Reviewed", slug='reviewed', workflow=self.work)
        State.objects.create(name_en="Rejected", slug='rejected', workflow=self.work)
        State.objects.create(name_en="Published", slug='published', workflow=self.work)
        State.objects.create(name_en="On top", slug='on-top', workflow=self.work)

        self.work.initial_state = State.objects.get(slug="draft")
        self.work.save()

    def create_basic_structure(self):
        states = dict([(state.name_en, state) for state in State.objects.all()])
        transitions = {}

        transitions['reviewed'] = Transition.objects.create(
            name_en="Review", slug='review',
            workflow=self.work, destination=states['Reviewed'])
        states['Draft'].transitions.add(transitions['reviewed'])

        transitions['rejected'] = Transition.objects.create(
            name_en="Reject", slug='reject', workflow=self.work,
            destination=self.work.states.get(slug="rejected"))
        states['Draft'].transitions.add(transitions['rejected'])

        transitions['modify'] = Transition.objects.create(
            name_en="Modify", slug='modify', workflow=self.work,
            destination=self.work.states.get(slug="draft"))
        states['Reviewed'].transitions.add(transitions['modify'])
        states['Rejected'].transitions.add(transitions['modify'])

        transitions['publish'] = Transition.objects.create(
            name_en="Publish", slug='publish', workflow=self.work,
            destination=self.work.states.get(slug="published"))
        states['Reviewed'].transitions.add(transitions['publish'])

        transitions['add_on_top'] = Transition.objects.create(
            name_en="Add on top", slug='add-on-top', workflow=self.work,
            destination=self.work.states.get(slug="on-top"))
        states['Reviewed'].transitions.add(transitions['add_on_top'])
        states['Published'].transitions.add(transitions['add_on_top'])

    def test_create_transitions_between_states(self):
        """
        """
        self.create_basic_structure()
        self.assertEquals(Transition.objects.count(), 5)

        states = dict([(state.name_en, state) for state in State.objects.all()])

        # First, checks that the transitions are correct
        self.assertEquals(set(states['Draft'].transitions.all()),
                          set([Transition.objects.get(slug='review'),
                               Transition.objects.get(slug='reject')]))

        self.assertEquals(set(states['Reviewed'].transitions.all()),
                          set([Transition.objects.get(slug='modify'),
                               Transition.objects.get(slug='publish'),
                               Transition.objects.get(slug='add-on-top')]))

        self.assertEquals(set(states['Rejected'].transitions.all()),
                          set([Transition.objects.get(slug='modify')]))

        self.assertEquals(set(states['Published'].transitions.all()),
                          set([Transition.objects.get(slug='add-on-top')]))

        self.assertEquals(set(states['On top'].transitions.all()),
                          set([]))

        # Now, we check the accesible states
        self.assertEquals(set(states['Draft'].get_all_states()),
                          set([states['Draft'], states['Reviewed'], states['Rejected']]))

        self.assertEquals(set(states['Reviewed'].get_all_states()),
                          set([states['Draft'], states['Published'],
                              states['On top'], states['Reviewed']]))

        self.assertEquals(set(states['Rejected'].get_all_states()),
                          set([states['Draft'], states['Rejected']]))

        self.assertEquals(set(states['Published'].get_all_states()),
                          set([states['On top'], states['Published']]))

        self.assertEquals(set(states['On top'].get_all_states()),
                          set([states['On top']]))

    def test_removing_states_throught_transitions(self):
        """
        This test covers the removing of some states of the workflow structure
        """
        self.create_basic_structure()
        self.assertEquals(State.objects.count(), 5)
        self.assertEquals(Transition.objects.count(), 5)
        aux_state = State.objects.get(slug='rejected')
        aux_state.delete()

        states = dict([(state.name_en, state) for state in State.objects.all()])

        self.assertEquals(Transition.objects.count(), 4)
        self.assertEquals(State.objects.count(), 4)

        # First, checks that the transitions are correct
        self.assertEquals(set(states['Draft'].transitions.all()),
                          set([Transition.objects.get(slug='review')]))

        self.assertEquals(set(states['Reviewed'].transitions.all()),
                          set([Transition.objects.get(slug='modify'),
                               Transition.objects.get(slug='publish'),
                               Transition.objects.get(slug='add-on-top')]))

        self.assertEquals(set(states['Published'].transitions.all()),
                          set([Transition.objects.get(slug='add-on-top')]))

        self.assertEquals(set(states['On top'].transitions.all()),
                          set([]))

        # Now, we check the accesible states
        self.assertEquals(set(states['Draft'].get_all_states()),
                          set([states['Draft'], states['Reviewed']]))

        self.assertEquals(set(states['Reviewed'].get_all_states()),
                          set([states['Draft'], states['Published'],
                              states['On top'], states['Reviewed']]))

        self.assertEquals(set(states['Published'].get_all_states()),
                          set([states['On top'], states['Published']]))

        self.assertEquals(set(states['On top'].get_all_states()),
                          set([states['On top']]))

        aux_state = State.objects.get(slug='published')
        aux_state.delete()

        states = dict([(state.name_en, state) for state in State.objects.all()])

        self.assertEquals(Transition.objects.count(), 3)
        self.assertEquals(State.objects.count(), 3)

        # First, checks that the transitions are correct
        self.assertEquals(set(states['Draft'].transitions.all()),
                          set([Transition.objects.get(slug='review')]))

        self.assertEquals(set(states['Reviewed'].transitions.all()),
                          set([Transition.objects.get(slug='modify'),
                               Transition.objects.get(slug='add-on-top')]))

        self.assertEquals(set(states['On top'].transitions.all()),
                          set([]))

        # Now, we check the accesible states
        self.assertEquals(set(states['Draft'].get_all_states()),
                          set([states['Reviewed'], states['Draft']]))

        self.assertEquals(set(states['Reviewed'].get_all_states()),
                          set([states['Draft'], states['On top'],
                               states['Reviewed']]))

        self.assertEquals(set(states['On top'].get_all_states()),
                          set([states['On top']]))

    def test_removing_transitions(self):
        """
        """
        self.create_basic_structure()
        self.assertEquals(State.objects.count(), 5)
        self.assertEquals(Transition.objects.count(), 5)

        some_transition = Transition.objects.get(slug='add-on-top')
        some_transition.delete()

        self.assertEquals(State.objects.count(), 5)
        self.assertEquals(Transition.objects.count(), 4)

        states = dict([(state.name_en, state) for state in State.objects.all()])

        # First, checks that the transitions are correct
        self.assertEquals(set(states['Draft'].transitions.all()),
                          set([Transition.objects.get(slug='review'),
                               Transition.objects.get(slug='reject')]))

        self.assertEquals(set(states['Reviewed'].transitions.all()),
                          set([Transition.objects.get(slug='modify'),
                               Transition.objects.get(slug='publish')]))

        self.assertEquals(set(states['Rejected'].transitions.all()),
                          set([Transition.objects.get(slug='modify')]))

        self.assertEquals(set(states['Published'].transitions.all()),
                          set([]))

        self.assertEquals(set(states['On top'].transitions.all()),
                          set([]))

        # Now, we check the accesible states
        self.assertEquals(set(states['Draft'].get_all_states()),
                          set([states['Reviewed'], states['Rejected'],
                               states['Draft']]))

        self.assertEquals(set(states['Reviewed'].get_all_states()),
                          set([states['Draft'], states['Published'],
                               states['Reviewed']]))

        self.assertEquals(set(states['Rejected'].get_all_states()),
                          set([states['Draft'], states['Rejected']]))

        self.assertEquals(set(states['Published'].get_all_states()),
                          set([states['Published']]))

        self.assertEquals(set(states['On top'].get_all_states()),
                          set([states['On top']]))

    def test_removing_transitions_origins(self):
        """
        """
        self.create_basic_structure()
        self.assertEquals(State.objects.count(), 5)
        self.assertEquals(Transition.objects.count(), 5)

        states = dict([(state.name_en, state) for state in State.objects.all()])
        transitions = dict([(transition.name_en, transition)
                            for transition in Transition.objects.all()])

        # Deattach some transitions between states
        states['Rejected'].transitions.remove(transitions['Modify'])
        states['Reviewed'].transitions.remove(transitions['Modify'])
        states['Reviewed'].transitions.remove(transitions['Add on top'])

        self.assertEquals(State.objects.count(), 5)
        self.assertEquals(Transition.objects.count(), 5)

        # First, checks that the transitions are correct
        self.assertEquals(set(states['Draft'].transitions.all()),
                          set([Transition.objects.get(slug='review'),
                               Transition.objects.get(slug='reject')]))

        self.assertEquals(set(states['Reviewed'].transitions.all()),
                          set([Transition.objects.get(slug='publish')]))

        self.assertEquals(set(states['Rejected'].transitions.all()),
                          set([]))

        self.assertEquals(set(states['Published'].transitions.all()),
                          set([Transition.objects.get(slug='add-on-top')]))

        self.assertEquals(set(states['On top'].transitions.all()),
                          set([]))

        # Now, we check the accesible states
        self.assertEquals(set(states['Draft'].get_all_states()),
                          set([states['Reviewed'], states['Rejected'],
                               states['Draft']]))

        self.assertEquals(set(states['Reviewed'].get_all_states()),
                          set([states['Published'], states['Reviewed']]))

        self.assertEquals(set(states['Rejected'].get_all_states()),
                          set([states['Rejected']]))

        self.assertEquals(set(states['Published'].get_all_states()),
                          set([states['On top'], states['Published']]))

        self.assertEquals(set(states['On top'].get_all_states()),
                          set([states['On top']]))

    def tearDown(self):
        self.work.delete()


class StatesAndPermissionTest(WorkflowBaseTestCase):
    """Checks the relation between states and permissions
    """

    def setUp(self):
        super(StatesAndPermissionTest, self).setUp()
        self.work = Workflow.objects.create(
            name_en='Foo Workflow', slug='foo-workflow')
        # after save the workflow is populated. We want a blank workflow
        self.work.blank()

        self.work.initial_state = None
        [state.delete() for state in self.work.states.all()]
        [transition.delete() for transition in self.work.transitions.all()]

        permissions = []
        permissions.append(Permission.objects.get(codename=u'can_draft'))
        permissions.append(Permission.objects.get(codename=u'can_pending'))
        permissions.append(Permission.objects.get(codename=u'can_published'))
        permissions.append(Permission.objects.get(codename=u'delete'))
        permissions.append(Permission.objects.get(codename=u'edit'))
        permissions.append(Permission.objects.get(codename=u'view'))

        for perm in permissions:
            self.work.add_permission(perm)

        self.work.set_to_model(ContentType.objects.get(name='document', app_label='section'))

        State.objects.create(name_en="Draft", slug='draft', workflow=self.work)
        State.objects.create(name_en="Reviewed", slug='reviewed', workflow=self.work)
        State.objects.create(name_en="Rejected", slug='rejected', workflow=self.work)
        State.objects.create(name_en="Published", slug='published', workflow=self.work)
        State.objects.create(name_en="On top", slug='on-top', workflow=self.work)

        self.work.initial_state = State.objects.get(slug="draft")
        self.work.save()

        states = dict([(state.name_en, state) for state in State.objects.all()])
        transitions = {}

        transitions['reviewed'] = Transition.objects.create(
            name_en="Review", workflow=self.work, destination=states['Reviewed'])
        states['Draft'].transitions.add(transitions['reviewed'])

        transitions['rejected'] = Transition.objects.create(
            name_en="Reject", workflow=self.work,
            destination=self.work.states.get(slug="rejected"))
        states['Draft'].transitions.add(transitions['rejected'])

        transitions['modify'] = Transition.objects.create(
            name_en="Modify", workflow=self.work,
            destination=self.work.states.get(slug="draft"))
        states['Reviewed'].transitions.add(transitions['modify'])
        states['Rejected'].transitions.add(transitions['modify'])

        transitions['publish'] = Transition.objects.create(
            name_en="Publish", workflow=self.work,
            destination=self.work.states.get(slug="published"))
        states['Reviewed'].transitions.add(transitions['publish'])

        transitions['add_on_top'] = Transition.objects.create(
            name_en="Add on top", workflow=self.work,
            destination=self.work.states.get(slug="on-top"))
        states['Reviewed'].transitions.add(transitions['add_on_top'])
        states['Published'].transitions.add(transitions['add_on_top'])

        # Some roles creation
        Role.objects.create(name='Editor', slug='editor')
        Role.objects.create(name='Revisor', slug='revisor')

    def test_relation_state_permission_role(self):
        """
        """
        # first, checks if the setUp is correct
        self.assertEquals(State.objects.count(), 5)
        self.assertEquals(Transition.objects.count(), 5)
        self.assertTrue(self.work.permissions.count() > 0)

        states = dict([(state.name_en, state)
                       for state in State.objects.all()])
        permissions = dict([(permission.codename, permission)
                       for permission in self.work.permissions.all()])
        roles = dict([(role.name, role) for role in Role.objects.all()])

        StatePermissionRelation.objects.create(
            state=states['Draft'], permission=permissions['view'],
            role=roles['Owner'])
        StatePermissionRelation.objects.create(
            state=states['Draft'], permission=permissions['edit'],
            role=roles['Owner'])
        StatePermissionRelation.objects.create(
            state=states['Draft'], permission=permissions['delete'],
            role=roles['Owner'])

        self.assertEquals(
            set(states['Draft'].get_permissions_by_role(roles['Owner'])),
            set([permissions['view'], permissions['edit'],
                 permissions['delete']]))

    def tearDown(self):
        self.work.delete()
