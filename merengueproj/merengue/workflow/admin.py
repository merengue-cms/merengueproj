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

from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import RelatedModelAdmin, BaseAdmin
from merengue.workflow.models import Workflow, State, Transition

from transmeta import get_fallback_fieldname


class WorkflowAdmin(BaseAdmin):
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}


class StateRelatedModelAdmin(RelatedModelAdmin):
    tool_name = 'states'
    tool_label = _('states')
    related_field = 'workflow'
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}


class TransitionRelatedModelAdmin(RelatedModelAdmin):
    tool_name = 'transitions'
    tool_label = _('transitions')
    related_field = 'workflow'
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}


def register_related(site):
    site.register_related(Transition, TransitionRelatedModelAdmin, related_to=Workflow)
    site.register_related(State, StateRelatedModelAdmin, related_to=Workflow)


def register(site):
    site.register(Workflow, WorkflowAdmin)
    register_related(site)
