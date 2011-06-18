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

from autoreports.model_forms import modelform_factory

from django.utils.translation import ugettext as _, ugettext_lazy

from merengue.block.blocks import ContentBlock
from plugins.smartsearch.forms import SearcherForm
from plugins.smartsearch.utils import get_fields
from merengue.collection.models import Collection


class SearchBlock(ContentBlock):
    name = 'searchform'
    default_place = 'aftercontent'
    help_text = ugettext_lazy('Block represents search widget')
    verbose_name = ugettext_lazy('Search block')
    default_caching_params = {
        'enabled': False,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def render(self, request, place, content, context, *args, **kwargs):
        if not isinstance(content, Collection):
            return ''
        searchers = content.searcher_set.all()
        forms_search = []
        for search in searchers:
            if not search.options:
                continue
            form_search_class = modelform_factory(model=search.content_type.model_class(),
                                                  form=SearcherForm)
            data = None
            if request.GET.get('__searcher'):
                data = request.GET
            fields = get_fields(search)
            if not fields:
                continue
            form_search_class.base_fields = get_fields(search)
            form_search = form_search_class(data=data, is_admin=False, search=search)
            if data:
                form_search.is_valid()
            forms_search.append(form_search)
        return self.render_block(request, template_name='smartsearch/block_search.html',
                                 block_title=_('Searchers'),
                                 context={'forms_search': forms_search})
