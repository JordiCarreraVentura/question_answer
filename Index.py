
from collections import (
    Counter,
    defaultdict as deft
)


class Index:

    def __init__(self, invprob):
        self.aa_by_w = deft(list)
        self.labels = []
        self.n = 0
        self.invprob = invprob
    
    def update(self, tokens):
        for w in set(tokens):
#         for w in tokens:
            self.aa_by_w[w].append(self.n)
        self.n += 1
    
    def add(self, label):
        self.labels.append(label)
    
    def crunch(self):
        for w, ii in self.aa_by_w.items():
            self.aa_by_w[w] = set(ii)
    
    def __call__(self, bow):
        hits = Counter()
        matched = deft(list)
        for w in set(bow):
            for i in self.aa_by_w[w]:
                if not self.invprob:
                    hits[i] += 1
                else:
                    hits[i] += self.invprob[w]
                matched[i].append(w)
        return [
            (f, i, self.labels[i], matched[i])
            for i, f in hits.most_common(10)
            if f
        ]
