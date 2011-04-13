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

from merengue.base.admin import BaseCategoryAdmin, BaseContentAdmin
from merengue.section.admin import SectionContentAdmin


class NewsCategoryAdmin(BaseCategoryAdmin):
    """ Admin for news item category management """


class NewsItemAdmin(BaseContentAdmin):
    """ Admin for news item management """
    list_display = BaseContentAdmin.list_display + ('publish_date', )
    list_filter = BaseContentAdmin.list_filter + ('categories', )
    html_fields = BaseContentAdmin.html_fields + ('body', )

    class Media:
        js = ('news/date_auto_fill.js', )


class NewsItemSectionAdmin(SectionContentAdmin, NewsItemAdmin):
    """ Admin for news item management inside sections """
    manage_contents = True
