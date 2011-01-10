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

from django import template
from django.utils.datastructures import SortedDict
from django.utils.functional import curry

from merengue.base.models import BaseContent
from merengue.multimedia.models import Photo

register = template.Library()


def _add_main_photos_relative_content(relative_contents, *args, **kwargs):
    for content in relative_contents:
        if content.main_image:
            photo_url = content.main_image.url
            yield dict(content_name=content.name,
                       content_url=content.get_absolute_url(),
                       photo_url=content.main_image.url,
                       photo_url_thumb=content.main_image.thumbnail.url(),
                       )

        else:
            photo_url = content.plone_image_link
            yield dict(content_name=content.name,
                       content_url=content.get_absolute_url(),
                       photo_url=photo_url,
                       photo_url_thumb=photo_url + '/image_thumb',
                       )


def _add_second_photos(relative_contents, photos_remaining, *args, **kwargs):
    bag = photos_remaining
    # Next line is a optimization hack. We use relative_contents_ids as subselect
    # note: order_by() in next sentence is intentional, to remove ordering in SQL
    # we need only one column in subselect (WHERE "id" in (SELECT "id" FROM ...))
    # Ordering causes to have to columns (see ticket #2397)
    relative_contents_ids = relative_contents.order_by().values('id').query
    if len(relative_contents_ids.get_columns()) != 1:
        # we ensure that won't execute a subselect with more than one column
        relative_contents_ids = [o.id for o in relative_contents]
    second_photos = Photo.objects.published().filter(basecontent__id__in=relative_contents_ids)\
                                             .exclude(multimediarelation__order=0)\
                                             .order_by("?").select_related("image")[:bag]
    for photo in second_photos:
        if photo.image:
            content = photo.basecontent_set.filter(id__in=relative_contents_ids)[0]
            yield dict(content_name=content.name,
                       content_url=content.get_absolute_url(),
                       photo_url=photo.image.url,
                       photo_url_thumb=photo.image.thumbnail.url(),
                       photo_caption=photo.caption,
                       )


class PhotosBag(object):

    def __init__(self, min_photos, max_photos, collectors=None):
        self._photos = SortedDict()
        self.min = min_photos
        self.max = max_photos
        self.collectors = collectors or []

    def add_collector(self, collector):
        """A collector is a callable return an iterator of photos.

        When the PhotosBag calls the collector it passes two arguments:
          - the destination object
          - the number of photos that can be added at this point
        """
        self.collectors.append(collector)

    def get_photos(self):
        size = len(self._photos)
        if size < self.min:
            photos = []
        elif size > self.max:
            photos = self._photos.values()[:self.max]
        else:
            photos = self._photos.values()

        return photos

    def collect_photos(self, *args, **kwargs):

        def photos_fetcher(max_photos):
            n_photos_collected = 0
            for collector in self.collectors:
                n_photos_remaining = max_photos - n_photos_collected
                for photo_info in collector(n_photos_remaining, *args, **kwargs):
                    photo_key = photo_info['photo_url']
                    if photo_key in self._photos:
                        continue

                    yield photo_key, photo_info

                    n_photos_collected += 1

                    if n_photos_collected > max_photos:
                        return

        for photo_key, photo_info in photos_fetcher(self.max):
            self._photos[photo_key] = photo_info

        return self.get_photos()


@register.inclusion_tag('base/photos_secundary_carousel.html', takes_context=True)
def carousel(context, contents, min_photos=5, max_photos=50):
    """
    This will put a carousel of destination and tourists resource images. "contents" parameter has to be a queryset of BaseContent objects

    Example usage::

        {% load slide_tags %}
        {% block content %}
          {% secundary_carousel location resources %}
        {% endblock %}
    """

    excludes = {'main_image': ''}
    if BaseContent == contents.model or BaseContent in contents.model._meta.parents:
        excludes['plone_image_link__isnull'] = True

    relative_contents = contents.exclude(**excludes).extra(select={'RANDOM': "RANDOM()"}).distinct().order_by("?")
    photos_bag = PhotosBag(min_photos, max_photos)

    photos_bag.add_collector(curry(_add_main_photos_relative_content, relative_contents))
    photos_bag.add_collector(curry(_add_second_photos, relative_contents))

    photos = photos_bag.collect_photos()

    return {'photos': photos,
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
            'request': context.get('request', None)}


@register.inclusion_tag('base/carousel.html', takes_context=True)
def carousel_simply(context, contents, min_photos=5, max_photos=50):
    """
    This will put a carousel of turist resource images. "contents" parameter has to be a queryset of BaseContent objects

    Example usage::

        {% load slide_tags %}
        {% block content %}
          {% carousel foo_contents %}
        {% endblock %}
    """

    contents = contents.exclude(plone_image_link__isnull=True, main_image='').distinct()

    if len(contents) < min_photos:
        contents = []
    elif len(contents) > max_photos:
        contents = contents.extra(select={'RANDOM': 'RANDOM()'}).order_by("?")[:max_photos]


    return {'contents': contents,
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
            'request': context.get('request', None)}
