
from Tools import (
    from_csv,
    ngrams,
    STOPWORDS,
    tokenizer,
    to_csv,
    unicode2ascii
)


class FeatureEngine:
    
    def __init__(self):
        return
    
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
        for token in tokens:
            for n in [4, 5, 6]:
#             for n in [4]:
                if token == 'PUNCT' or token in STOPWORDS['es']:
                    continue
                elif len(token) <= n:
                    grams.append(token)
                else:
                    grams += [''.join(g) for g in ngrams(token, n)]
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
        return grams
