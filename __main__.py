import json

from collections import (
    Counter,
    defaultdict as deft
)

from Classifier import Classifier

from Dataset import Dataset

from FeatureEngine import FeatureEngine

from Index import Index

from InverseProbabilities import InverseProbabilities

from Tools import (
    normalize,
#     STOPWORDS,
    to_csv,
    tokenizer,
    words
)

# from Workflow import (
#     partition_dataset
# )



KEYS = ('Question', 'Topic', 'Correct', 'Predicted', 'Gold')


fe = FeatureEngine()
# fe = FeatureEngine(ngrams=True, ch_ngrams=False)
# fe = FeatureEngine(ngrams=True, ch_ngrams=False)

def bow(text, prob_filter=None):
    if not prob_filter:
#         return fe(' '.join(words(text)))
        return words(text)
    else:
        prob_words = sorted([(prob_filter[w], w) for w in words(text)])
#         return fe(' '.join([w for p, w in prob_words[-int(len(prob_words) * 0.8):]]))
        return [w for p, w in prob_words[-int(len(prob_words) * 0.8):]]



if __name__ == '__main__':

    dataset = Dataset(
        '/Users/jordi/Laboratorio/corpora/anotados/Microsoft-WikiQA-corpus/WikiQACorpus/WikiQA.tsv'
        )
    dataset.load()

#     fe = FeatureEngine(ngrams=True)
#     fe = FeatureEngine()
    cls = Classifier()
    invprob = InverseProbabilities(dataset)
    index = Index(invprob)

    train = [
#         (bow(label, prob_filter=invprob) + bow(text, prob_filter=invprob), label, mark)
        (bow(text, prob_filter=invprob), label, mark)
        for text, label, mark in dataset.train()
    ]

    test = [
        (bow(label, prob_filter=invprob), label, mark)
        for text, label, mark in dataset.test()
        if mark
    ][:int(len(train) * 0.4)]

    test += [
        (bow(label, prob_filter=invprob), label, mark)
        for text, label, mark in dataset.test()
        if not mark
    ][:len(test)]

    for tbow, label, mark in train:
        index.update(tbow)
        index.add(label)

    tp, tn, fp, fn = 0, 0, 0, 0
    marked = sum([1 for _, _, mark in test if mark])
    for tbow, label, mark in test:
        expectation = sum([invprob[w] for w in set(bow(label, prob_filter=invprob))])
        matches = index(tbow)

        if not matches and not mark:
            tn += 1
            continue
        elif not matches and mark:
            fn += 1
            continue

        best_match = matches[0]
        guess = best_match[2]
        sim = best_match[0]
        ratio = sim / expectation

        if ratio <= 0.9:
            if not mark:
                tn += 1
            else:
                fn += 1
        else:
            if mark and guess == label:
                tp += 1
            elif mark:
                fp += 1

        if tp:
            prec = tp / float(tp + fp)
            rec = tp / float(tp + fn)
        else:
            prec, rec = 0.0, 0.0

        print label
        print words(label)
        print expectation
        for x in matches[:5]:
            print '\t', x[0] / expectation, x
        print 'tp: %d, tn: %d, fp: %d, fn: %d, all: %d, prec: %.2f, rec: %.2f' % (tp, tn, fp, fn, sum([tp, tn, fp, fn]), prec, rec)
        print
#         raw_input()
#     exit()


    exit()


    train = [
        (' '.join(fe(text)), label, mark)
        for text, label, mark in dataset.train()
    ]

    test = [
        (' '.join(fe(text)), label, mark)
        for text, label, mark in dataset.test()
        if mark
    ]

    test += [
        (' '.join(fe(text)), label, mark)
        for text, label, mark in dataset.test()
        if not mark
    ][:len(test)]

    cls.train(train)

    tp, tp3, hits, hits3 = 0, 0, 0, 0
    report = []
    randoms = []
    for i, guesses in enumerate(cls.test(test)):
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
