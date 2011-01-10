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


class ChunksManager(models.Manager):

    def placed_at(self, place, url_query):
        chunks = super(ChunksManager, self).filter(models.Q(placed_at=place) | models.Q(placed_at='all'))
        chunks_id = [chunk.id for chunk in chunks if chunk.match_with_url(url_query)]
        return chunks.filter(id__in=chunks_id)
