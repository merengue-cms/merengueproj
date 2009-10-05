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
