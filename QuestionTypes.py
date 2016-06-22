
from collections import (
    Counter,
    defaultdict as deft
)


ROWS_KEYS = [
    ('ProbabilityOverErrors', 'ErrorType',
     'QuestionType', 'ProbabilityOverOccurrences')
]


class QuestionTypes:


    def __init__(self):
        self.unimass = deft(float)
        self.bimass = deft(float)
        self.unigrams = Counter()
        self.bigrams = Counter()
        self.umass = 0.0
        self.bmass = 0.0


    def increment(self, label):
        uni, bi = self(label)
        self.unimass[uni] += 1
        self.bimass[bi] += 1

    
    def __call__(self, label):
        tokens = label.lower().split()
        return tokens[0], '_'.join(tokens[:2])


    def update(self, error, guess, actual):
        uni, bi = self(actual)
        if not guess:
            self.unigrams[(error, uni)] += 1
            self.bigrams[(error, bi)] += 1
        else:
            self.unigrams[(error, uni)] += 1
            self.bigrams[(error, bi)] += 1
    

    def __mass(self):
        self.umass = float(sum(self.unigrams.values()))
        self.bmass = float(sum(self.bigrams.values()))


    def dump(self):

        rows = []
        self.__mass()

        for (error, qtype), f in self.unigrams.most_common():
            ratio = f / self.unimass[qtype]
            incidence = f / self.umass
            row = (incidence, error, qtype, ratio)
            rows.append(row)

        for (error, qtype), f in self.bigrams.most_common():
            ratio = f / self.bimass[qtype]
            incidence = f / self.bmass
            row = (incidence, error, qtype, ratio)
            rows.append(row)

        return sorted(ROWS_KEYS + rows, reverse=True)
