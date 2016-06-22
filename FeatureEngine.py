
from collections import defaultdict as deft

from Tools import (
    from_csv,
    ngrams,
    STOPWORDS,
    tokenizer,
    to_csv,
    unicode2ascii
)


EXCEPTIONS = {
    'en': ['how', 'what', 'who', 'where', 'when']
}


class FeatureEngine:

    def __init__(self, ch_ngrams=True, ngrams=False, lang='en'):
        self.lang = lang
        self._ngrams = ngrams
        self._ch_ngrams = ch_ngrams
        self.stopwords = deft(bool)
        for w in STOPWORDS[self.lang]:
            if w not in EXCEPTIONS[self.lang]:
                self.stopwords[w] = True

    def __call__(self, string):
        space = unicode2ascii(string.lower())
#         print 1, space
        tokens = tokenizer(space, alnum=False)
#         print 2, tokens
        grams = self.__grams(tokens)
#         print 3, grams
        return grams

    def __grams(self, tokens):
        grams = []
        if self._ch_ngrams:
            for token in tokens:
                for n in [4, 5, 6]:
    #             for n in [4]:
    #                 if token == 'PUNCT' or \
    #                 self.stopwords[token] or \
    #                 not token.isalpha():
    #                     continue
    #                 if token == 'PUNCT' or \
    #                 self.stopwords[token]:
    #                     continue
                    if token == 'PUNCT':
                        continue
                    elif len(token) <= n:
                        grams.append(token)
                    else:
                        grams += [''.join(g) for g in ngrams(token, n)]
        if not self._ngrams:
            return grams
        for n in [2, 3, 4]:
#         for n in [2]:
            _grams = ngrams(tokens, n)
            for _g in _grams:
                if 'PUNCT' in _g:
                    continue
                elif n > 2:
                    grams.append(' '.join([_g[0], '*', _g[-1]]))
                else:
                    grams.append(' '.join(_g))
#         grams = self.__sequence_deduplication(grams)
        return grams

    def __sequence_deduplication(self, grams):
        new = []
        prev = None
        for gram in grams:
            if gram == prev:
                continue
            new.append(gram)
            prev = gram
        return new
