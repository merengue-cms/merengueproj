# Copyright (c) 2011 by Yaco Sistemas
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

from django.contrib.contenttypes.models import ContentType

from merengue.base.models import Base, BaseContent
from merengue.workflow.models import State, WorkflowModelRelation, Workflow


def workflow_by_model(model):
    """Fetch what workflow is the one used by the given model,
    looking the parents if it's needed
    """
    if model == Base:
        # the recursion has not found any workflow (this can happend in testing environment
        # because all the relations between workflow and models as been deleted. In this
        # weird circunstances we will return the default workflow
        return Workflow.objects.default_workflow()
    if model._meta.abstract:
        # find the first non abstract model because abstract models have not contenttypes
        for base in model.__bases__:
            if not base._meta.abstract:
                model = base
                break
    content_type = ContentType.objects.get(model=model._meta.module_name, app_label=model._meta.app_label)
    try:
        return WorkflowModelRelation.objects.get(content_type=content_type).workflow
    except WorkflowModelRelation.DoesNotExist:
        # we look for the parent
        if BaseContent in content_type.model_class().mro():
            for base in model.__bases__:
                return workflow_by_model(base)
        else:  # this content type has no a workflow, and will not fetch from base content
            return Workflow.objects.default_workflow()


def change_status(content, state):
    """ change the status of a content """
    workflow = workflow_by_model(content.__class__)
    status = workflow.states.get(slug=state)
    content.workflow_status = status
    content.save()


def update_objects_permissions():
    """ update all the contents permissions """
    models = BaseContent.get_subclasses()
    for model in models:
        print 'Updating model: %s' % model
        queryset = model.objects.all()
        update_queryset_permissions(queryset)


def update_queryset_permissions(queryset):
    """ update all the permissions in the queryset objects """
    for content in queryset:
        print ' Updating permissions in content: %s' % content
        if not content.workflow_status:  # we need to set the proper state objetc
            print '  Adding workflow.State object'
            if hasattr(content, 'get_real_instance'):
                content = content.get_real_instance()
            workflow = workflow_by_model(type(content))
            content.workflow_status = State.objects.get(workflow=workflow,
                                                        slug=content.status)
        content.update_status()
