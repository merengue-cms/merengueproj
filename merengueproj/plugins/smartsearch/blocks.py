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

from autoreports.models import modelform_factory

from django.utils.translation import ugettext as _, ugettext_lazy

from merengue.block.blocks import ContentBlock
from plugins.smartsearch.forms import SearcherForm
from merengue.collection.models import Collection


class SearchBlock(ContentBlock):
    name = 'searchform'
    default_place = 'aftercontent'
    help_text = ugettext_lazy('Block represents search widget')
    verbose_name = ugettext_lazy('Search block')

    @classmethod
    def render(cls, request, place, content, context, *args, **kwargs):
        if not isinstance(content, Collection):
            return ''
        searchers = content.searcher_set.all()
        forms_search = []
        for search in searchers:
            form_search_class = modelform_factory(model=search.content_type.model_class(),
                                                  form=SearcherForm)
            data = None
            if request.GET.get('__searcher'):
                data = request.GET
            form_search = form_search_class(data=data, fields=search.report_filter_fields_tuple, is_admin=False, report=search)
            if data:
                form_search.is_valid()
            forms_search.append(form_search)
        return cls.render_block(request, template_name='smartsearch/block_search.html',
                                block_title=_('Searchers'),
                                context={'forms_search': forms_search})
