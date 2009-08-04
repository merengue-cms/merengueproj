"""
Based on search algorithms from Armand Lynch <lyncha@users.sourceforge.net>.
To see original algorithms, go to http://celljam.net/
"""
import Levenshtein


class WordNotFound(Exception):
    """
    Device Not Found exception class

    Raised when cannot find a word by using either select_*
    API functions.
    """
    pass


class Algorithm(object):
    """
    Base class for all search algorithms
    """

    def __call__(self, query, words):
        """
        Every algorithm class must define a __call__ method.

        @param query: The query
        @type query: string
        @param words: The words object to search
        @type words: list
        @rtype: string
        """
        raise NotImplementedError


class JaroWinkler(Algorithm):
    """
    Jaro-Winkler Search Algorithm
    """

    def __init__(self, accuracy=0.75, weight=0.05):
        """
        @param accuracy: The tolerance that the Jaro-Winkler algorithm will
                            use to determine if a query matches
                            0.0 <= accuracy <= 1.0
        @type accuracy: float
        @param weight: The prefix weight is inverse value of common prefix
                        length sufficient to consider the strings
                        'identical' (excerpt from the Levenshtein module
                        documentation).
        @type weight: float
        """

        self.accuracy = accuracy
        self.weight = weight

    def __call__(self, query, words):
        """
        @param query: The query
        @type query: string
        @param words: The words object to search
        @type words: list
        @rtype: string
        @raises WordNotFound
        """
        match = self.__get_match(query, words)
        if match:
            match.sort(key=lambda x: x[0], reverse=True)
            return match
        else:
            raise WordNotFound(query)

    def __get_match(self, query, words):
        _match = []
        for word in words:
            distance = Levenshtein.jaro_winkler(word, query, self.weight)
            if distance > self.accuracy:
                _match.append((distance, word))
        return _match


class LevenshteinDistance(Algorithm):
    """
    Levenshtein distance Search Algorithm
    """

    def __init__(self, accuracy_letter=4):
        self.accuracy_letter = accuracy_letter

    def __call__(self, query, words):
        """
        @param query: The query
        @type query: string
        @param words: The devices object to search
        @type words: list
        @rtype: string
        """
        match = self.__get_match(query, words)
        match.sort(key=lambda x: x[0])
        return match

    def __get_match(self, query, words):
        _match = []
        for word in words:
            distance = Levenshtein.distance(query, word)
            if distance < self.accuracy_letter:
                _match.append((distance, word))
        return _match
