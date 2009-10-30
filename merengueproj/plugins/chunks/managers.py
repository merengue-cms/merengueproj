from django.db import models


class ChunksManager(models.Manager):

    def placed_at(self, place, url_query):
        chunks = super(ChunksManager, self).filter(models.Q(placed_at=place) | models.Q(placed_at='all'))
        chunks_id = [chunk.id for chunk in chunks if chunk.match_with_url(url_query)]
        return chunks.filter(id__in=chunks_id)
