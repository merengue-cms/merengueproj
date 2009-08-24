from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class SearchFilter(forms.Form):

    def __init__(self, show_city_field=False, filters={}, *args, **kwargs):
        super(SearchFilter, self).__init__(*args, **kwargs)
        self.fields['name__icontains'] = forms.CharField(max_length=30,
                               widget=forms.TextInput(),
                               label=_(u'Name'),
                               required=False)
        self._recommended_other_words = []
        self.filters = filters or {}

    def recommended_other_words(self, contents, recursive=False):
        from merengue.base.search_word import LevenshteinDistance, JaroWinkler
        if not contents:
            if settings.SEARCH_ALGORITHM == 'JAROWINKLER':
                searcher_words = JaroWinkler(**settings.PROPERTIES_JAROWINKLER)
            else:
                searcher_words = LevenshteinDistance(
                                            **settings.PROPERTIES_LEVENTEIN)
            word = self.cleaned_data.get('name__icontains')
            word_cities = self.cleaned_data.get(
                                        'location__cities__name__icontains')
            if word and not recursive:
                words = [x.name for x in contents.model.objects.filter(
                                                            **self.filters)]
                self.recommended_field = 'name__icontains'
            else:
                words = []
            words = list(set(words).union(
                                self._split_recommended_words(words)))
            recommended_words = searcher_words(query=word, words=words)
            if not word in dict(recommended_words).values():
                self._recommended_other_words = recommended_words
            else:
                self.recommended_other_words(contents, recursive=True)

    def _split_recommended_words(self, words):
        s = set()
        for phrase in words:
            word_list = phrase.split()
            if len(word_list) > 1:
                s = s.union(set(
                        [word for word in word_list if len(word) > 3]))
        return s

    def get_words_recommended(self):
        return self._recommended_other_words
