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

from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import RelatedModelAdmin
from django.contrib.contenttypes.models import ContentType

from merengue.collection.models import Collection

from plugins.smartsearch.forms import SearcherRelatedCollectionModelAdminForm
from plugins.smartsearch.models import Searcher


class SearcherRelatedCollectionAdmin(RelatedModelAdmin):
    tool_name = 'searcher_related'
    tool_label = _('searcher related')
    related_field = 'collections'
    form = SearcherRelatedCollectionModelAdminForm

    def add_view(self, request, form_url='', extra_context=None, parent_model_admin=None, parent_object=None):
        form_top_class = self.get_form(request)
        content_type_model = self.basecontent.get_first_parents_of_content_types()
        content_type = ContentType.objects.get_for_model(content_type_model)
        extra_context = self._update_extra_context(request, extra_context, parent_model_admin, parent_object)
        context = {'model_admin': self,
                   'columns': {'fields': True,
                               'filter': True,
                               'display': False,
                               'help_text': True,
                               'advanced_options': True}, }
        context.update(extra_context)
        return self.report_api_wizard(request,
                                      queryset=None, template_name='smartsearch/smartsearch_adminwizard.html',
                                      extra_context=context,
                                      model=Searcher,
                                      form_top_class=form_top_class,
                                      content_type=content_type)

    def _create_report(self, model, name, report_display_fields,
                            report_filter_fields, content_type, report_advance):
        searcher = super(SearcherRelatedCollectionAdmin, self)._create_report(model, name, report_display_fields,
                                                                              report_filter_fields, content_type,
                                                                              report_advance)
        if isinstance(searcher, Searcher):
            searcher.collections.add(self.basecontent)
        return searcher

    def get_form(self, request, obj=None, **kwargs):
        form = super(SearcherRelatedCollectionAdmin, self).get_form(request, obj, **kwargs)
        form.collection = self.basecontent
        return form

    def save_form(self, request, form, change):
        # we associate related object
        if form.instance.id:
            collections = list(form.instance.collections.all())
            collections.append(self.basecontent)
        else:
            collections = [self.basecontent]
        form.cleaned_data[self.related_field] = collections
        return super(RelatedModelAdmin, self).save_form(request, form, change)


def register(site):
    """ Merengue admin registration callback """
    site.register_related(Searcher, SearcherRelatedCollectionAdmin, related_to=Collection)


def unregister(site):
    """ Merengue admin unregistration callback """
    pass
