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

from searchform.terms import MultipleOptionsSearchTerm


class ClassSearchTerm(MultipleOptionsSearchTerm):

    def _options(self):
        from merengue.base.models import BaseContent
        return [(c, _(c)) for c in BaseContent.objects.different_class_names()]

    options = property(_options)

    def _get_value_text(self, value):
        options_map = dict(self.options)
        value_text = [unicode(options_map[val]) for val in value]
        return u', '.join(value_text)

    def get_query_arg_as_text(self, operator, value):
        if value == '':
            return ''
        value_text = self._get_value_text(value)
        return u'%s %s' % (self.get_description(operator), value_text)


class OptionDistinctTerm(object):

    def _options(self):
        empty = []
        if self.has_empty_option:
            empty.append(('', '----------'))
        queryset = self.model.objects.filter(**self.filters).distinct()
        return empty + [(obj.id, unicode(obj)) for obj in queryset]
    options = property(_options)


class BindableSearchTerm(object):

    def __init__(self, *args, **kwargs):
        super(BindableSearchTerm, self).__init__(*args, **kwargs)
        self.filters = {}

    def queryset(self):
        manager = self.model.objects
        if hasattr(manager, 'published'):
            return manager.published()
        else:
            return manager.all()

    def _options(self):
        empty = []
        if self.has_empty_option:
            empty.append(('', '----------'))

        queryset = self.queryset()

        if self.filters:
            queryset = queryset.filter(**self.filters)

        return empty + [(obj.id, unicode(obj)) for obj in queryset]

    options = property(_options)
