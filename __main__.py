import json

from Classifier import Classifier

from Dataset import Dataset

from FeatureEngine import FeatureEngine

from Workflow import (
    partition_dataset
)


if __name__ == '__main__':

    dataset = Dataset(
        '/Users/jordi/Laboratorio/corpora/anotados/Microsoft-WikiQA-corpus/WikiQACorpus/WikiQA.tsv'
        )
    dataset.load()

    fe = FeatureEngine()
    cls = Classifier()
    train, test = partition_dataset(dataset, fe, min_ctxt=5, n_macros=300)

    cls.train(train)
    tp, tp3 = 0, 0
    for i, guesses in enumerate(cls.test(test)):
#         print test[i]
#         print guess[:5]
        gold = test[i][1]
        if gold in [label for prob, label in guesses[:1]]:
            tp += 1
            tp3 += 1
            print tp, tp3, len(test), round(tp / float(len(test)), 4), round(tp3 / float(len(test)), 4)
        elif gold in [label for prob, label in guesses[:3]]:
            tp3 += 1
            print tp, tp3, len(test), round(tp / float(len(test)), 4), round(tp3 / float(len(test)), 4)
#         else:
#             print test[i][2], '\t', test[i][1]
#             print guesses[:10]
#             raw_input()
