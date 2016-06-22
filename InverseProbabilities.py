
from collections import (
    Counter,
    defaultdict as deft
)

from Tools import words


class InverseProbabilities:
    
    def __init__(self, dataset):
        self.mass = 0.0
        self.freq = Counter()
        for text, _, _ in dataset.train():
            tokens = words(text)
            self.freq.update(tokens)
            self.mass += len(tokens)
    
    def __getitem__(self, w):
        return self.mass / (self.freq[w] + 1.0)
