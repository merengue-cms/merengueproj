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

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import transaction

from transmeta import get_real_fieldname
from merengue.pluggable import Plugin
from merengue.collection.models import (Collection, IncludeCollectionFilter,
                                        CollectionDisplayField,
                                        CollectionDisplayFieldFilter)


from plugins.link.admin import LinkAdmin, LinkCategoryAdmin, LinkSectionAdmin
from plugins.link.models import Link, LinkCategory
from plugins.link.viewlets import LatestLinkViewlet, AllLinkViewlet


class PluginConfig(Plugin):
    name = 'Links'
    description = 'Links plugin'
    version = '0.0.1a'

    url_prefixes = (
        ('link', 'plugins.link.urls'),
    )

    @classmethod
    def section_models(cls):
        return [(Link, LinkSectionAdmin)]

    @classmethod
    def get_model_admins(cls):
        return [(Link, LinkAdmin), (LinkCategory, LinkCategoryAdmin)]

    @classmethod
    def get_viewlets(cls):
        return [LatestLinkViewlet, AllLinkViewlet]

    @classmethod
    def hook_post_register(cls):

        def create_collection(slug, name, model, create_display_field=True, create_filter_field=True):
            ct = ContentType.objects.get_for_model(model)
            sp = transaction.savepoint()
            collection, created = Collection.objects.get_or_create(slug=slug)
            transaction.savepoint_commit(sp)

            if created:
                collection.status = 'published'
                collection.no_changeable_fields = ['slug']
                collection.no_deletable = True
                setattr(collection, get_real_fieldname('name', settings.LANGUAGE_CODE), name)
                collection.save()

                if create_filter_field:
                    IncludeCollectionFilter.objects.create(collection=collection,
                                                        filter_field='status',
                                                        filter_operator='exact',
                                                        filter_value='published')
                if create_display_field:
                    dfield = CollectionDisplayField.objects.create(field_name='description',
                                                                safe=True,
                                                                show_label=False,
                                                                collection=collection)
                    CollectionDisplayFieldFilter.objects.create(display_field=dfield,
                                                                filter_module='django.template.defaultfilters.truncatewords_html',
                                                                filter_params='15')
                collection.content_types.add(ct)

        create_collection('links', u'Links', Link,
                          create_display_field=True, create_filter_field=True)
