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

from merengue.registry import params

from plugins.banner.models import Banner


def get_banners_choices():
    return [(c.pk, c.name) for c in Banner.objects.all()]


class BannerParam(params.Param):

    def __init__(self, *args, **kwargs):
        super(BannerParam, self).__init__(*args, **kwargs)
        if 'choices' not in kwargs:
            self.choices = get_banners_choices

    def is_valid(self, value):
        return super(BannerParam, self).is_valid(value) and \
               Banner.objects.filter(pk=value)

    def get_value(self):
        value = super(BannerParam, self).get_value()
        if value:
            return int(value)
        return value

    def get_obj(self):
        value = self.get_value()
        try:
            return Banner.objects.get(pk=value)
        except Banner.DoesNotExist:
            return None
