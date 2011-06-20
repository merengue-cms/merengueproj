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

import sorl
from merengue.base.admin import BaseCategoryAdmin, BaseContentAdmin
from merengue.section.admin import SectionContentAdmin
from plugins.banner.models import Banner


class BannerCategoryAdmin(BaseCategoryAdmin):
    """ Admin for news item category management """


class BannerAdmin(BaseContentAdmin):

    def save_model(self, request, obj, form, change):
        saved = super(BannerAdmin, self).save_model(request, obj, form, change)
        # if we changed the image, its thumbnail is no longer valid.
        if obj.id and 'image' in form.changed_data:
            sorl.thumbnail.delete(obj.image, delete_file=False)
        return saved


class BannerSectionAdmin(SectionContentAdmin, BannerAdmin):
    manage_contents = True


def register(site):
    """ Merengue admin registration callback """
    site.register(Banner, BannerAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Banner)
