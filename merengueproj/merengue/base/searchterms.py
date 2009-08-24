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
