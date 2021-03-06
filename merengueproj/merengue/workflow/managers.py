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
from django.db.models.query import QuerySet

from merengue.workflow import DEFAULT_WORKFLOW


class WorkflowQuerySet(QuerySet):

    def default_workflow(self):
        return self.get(slug=DEFAULT_WORKFLOW)


class WorkflowManager(models.Manager):
    """ Workflow manager """

    def get_query_set(self):
        return WorkflowQuerySet(self.model)

    def default_workflow(self):
        return self.get_query_set().default_workflow()
