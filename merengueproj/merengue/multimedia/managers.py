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

from django.db import connection

from merengue.base.managers import WorkflowManager


class MultimediaManager(WorkflowManager):
    """ multimedia resources manager """

    def by_model(self, model):
        """
        Does a join with exact child multimedia model for select only those objects

        For example, with model="photo", sql below works out to the following (simplified):
           SELECT multimedia_basemultimedia.*
           FROM "multimedia_basemultimedia", "base_multimedia_photo"
           WHERE ...
           AND "multimedia_photo"."basemultimedia_ptr_id" = "multimedia_basemultimedia"."id"
        """
        qn = connection.ops.quote_name
        table = qn("multimedia_%s" % model)
        queryset = self.extra(tables=[qn(table)],
            where=['%s.%s = %s.%s' % \
                (qn(table), qn("basemultimedia_ptr_id"), qn("multimedia_basemultimedia"), qn("id"))]).distinct()

        def published():
            return queryset.filter(status='published')
        queryset.published = published
        return queryset

    def photos(self):
        """ only returns photos """
        return self.by_model("photo")

    def videos(self):
        """ only returns videos """
        return self.by_model("video")

    def panoramic_views(self):
        """ only returns panoramic views """
        return self.by_model("panoramicview")

    def images3d(self):
        """ only returns 3d images """
        return self.by_model("image3d")

    def files(self):
        """ only returns files """
        return self.by_model("file")
