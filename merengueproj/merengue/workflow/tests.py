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

from merengue.perms.models import Permission
from merengue.workflow.models import (Workflow, State, Transition,
                                      WorkflowModelRelation,
                                      WorkflowPermissionRelation)


class WorkflowBasicTest(TestCase):
    """This TestCase will test the most simplest aspect
    of Workflow model.
    """

    def setUp(self):
        pass

    def test_basic_creation(self):
        """Test the creation of a empty Workflow object.
        """
        self.assertEquals(Workflow.objects.count(), 0)
        Workflow.objects.create(name='foo workflow')
        Workflow.objects.create(name='bar workflow')
        self.assertEquals(Workflow.objects.count(), 2)
        self.assertEquals(State.objects.count(), 0)
        self.assertEquals(Transition.objects.count(), 0)

        work = Workflow.objects.get(name='foo workflow')
        self.assertEquals(work.id, 1)
        self.assertEquals(work.permissions.count(), 0)
        self.assertEquals(work.states.count(), 0)
        self.assertEquals(work.transitions.count(), 0)
        self.assertEquals(work.initial_state, None)

    def test_workflow_permission_relation(self):
        """Test the relationship between a Workflow and the permissions
        associated with them.
        """
        work = Workflow.objects.create(name='foo workflow')

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
        work = Workflow.objects.create(name='foo workflow')
        doc = ContentType.objects.get(name='document')

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
        new_work = Workflow.objects.create(name="bar workflow")
        new_work.set_to_model(video)
        self.assertEquals(WorkflowModelRelation.objects.count(), 2)
        relation_2 = WorkflowModelRelation.objects.all()[1]
        self.assertEquals(relation_2.content_type_id, video.id)
        self.assertEquals(relation_2.workflow_id, new_work.id)

    def test_workflow_creation_and_delete(self):
        work = Workflow.objects.create(name='foo workflow')

        permissions = []
        permissions.append(Permission.objects.get(codename=u'can_draft'))
        permissions.append(Permission.objects.get(codename=u'can_pending'))
        permissions.append(Permission.objects.get(codename=u'can_published'))
        permissions.append(Permission.objects.get(codename=u'delete'))
        permissions.append(Permission.objects.get(codename=u'edit'))
        permissions.append(Permission.objects.get(codename=u'view'))

        for perm in permissions:
            work.add_permission(perm)

        work.set_to_model(ContentType.objects.get(name='document'))

        self.assertEquals(work.permissions.count(), 6)
        self.assertEquals(WorkflowPermissionRelation.objects.count(), 6)
        self.assertEquals(WorkflowModelRelation.objects.count(), 1)
        work.delete()
        self.assertEquals(WorkflowPermissionRelation.objects.count(), 0)
        self.assertEquals(WorkflowModelRelation.objects.count(), 0)

    def tearDown(self):
        pass


class WorkflowStatesBasicTest(TestCase):
    """Tests about the relation between Workflow and State objects.
    """

    def setUp(self):
        """With this setting up, we instance a basic Workflow
        with some perms that will be manage by it, and a ContentType
        that will use that Workflow
        """
        self.work = Workflow.objects.create(name='foo workflow')

        permissions = []
        permissions.append(Permission.objects.get(codename=u'can_draft'))
        permissions.append(Permission.objects.get(codename=u'can_pending'))
        permissions.append(Permission.objects.get(codename=u'can_published'))
        permissions.append(Permission.objects.get(codename=u'delete'))
        permissions.append(Permission.objects.get(codename=u'edit'))
        permissions.append(Permission.objects.get(codename=u'view'))

        for perm in permissions:
            self.work.add_permission(perm)

        self.work.set_to_model(ContentType.objects.get(name='document'))

    def test_basic_states_creation(self):
        """Test the creation of some states for the Workflow
        """
        self.assertEquals(State.objects.count(), 0)
        State.objects.create(name="Draft", workflow=self.work)
        State.objects.create(name="Reviewed", workflow=self.work)
        State.objects.create(name="Rejected", workflow=self.work)
        State.objects.create(name="Published", workflow=self.work)
        State.objects.create(name="On top", workflow=self.work)

        self.assertEquals(State.objects.count(), self.work.states.count())

        gen_states_name = [state.name for state in State.objects.all()]
        work_states_name = [state.name for state in self.work.states.all()]

        gen_states_name.sort()
        work_states_name.sort()
        self.assertEquals(gen_states_name, work_states_name)

    def test_set_initial_state(self):
        """Test to check the proper setting of a initial state for the workflow
        """
        State.objects.create(name="Reviewed", workflow=self.work)
        State.objects.create(name="Draft", workflow=self.work)
        State.objects.create(name="Rejected", workflow=self.work)
        State.objects.create(name="Published", workflow=self.work)
        State.objects.create(name="On top", workflow=self.work)

        self.assertEquals(self.work.get_initial_state(),
                          self.work.states.all()[0])

        self.work.initial_state = State.objects.get(name="Draft")
        self.assertEquals(self.work.get_initial_state(),
                          self.work.states.all()[1])

    def test_get_initial_state_from_content_type(self):
        """Test if it's possible to get the initial state of a workflow
        accessing through ContentType
        """
        State.objects.create(name="Draft", workflow=self.work)
        State.objects.create(name="Reviewed", workflow=self.work)
        State.objects.create(name="Rejected", workflow=self.work)
        State.objects.create(name="Published", workflow=self.work)
        State.objects.create(name="On top", workflow=self.work)

        self.work.initial_state = State.objects.get(name="Draft")
        self.work.save()

        doc = ContentType.objects.get(name='document')
        obtained_workflow = WorkflowModelRelation.objects.get(
            content_type=doc).workflow

        self.assertEquals(self.work.initial_state,
                          obtained_workflow.get_initial_state())

    def test_removing_initial_state(self):
        """Test that the workflow behaviour is correct after removing the
        initial state.
        """
        State.objects.create(name="Draft", workflow=self.work)
        State.objects.create(name="Reviewed", workflow=self.work)
        State.objects.create(name="Rejected", workflow=self.work)
        State.objects.create(name="Published", workflow=self.work)
        State.objects.create(name="On top", workflow=self.work)

        self.work.initial_state = State.objects.get(name="Draft")
        self.work.save()

        self.assertEquals(self.work.get_initial_state(),
                          self.work.states.all()[0])
        self.assertEquals(self.work.get_initial_state().name, "Draft")
        State.objects.get(name="Draft").delete()
        self.assertEquals(self.work.get_initial_state(),
                          self.work.states.all()[0])
        self.assertEquals(self.work.get_initial_state().name, "Reviewed")

    def test_removing_all_states(self):
        """Test that the workflow behaviour is correct after removing
        all the states.
        """
        self.assertEquals('TODO', False)

    def tearDown(self):
        self.work.delete()

        pass
