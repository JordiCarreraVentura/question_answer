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
    average as avg,
    f1,
    normalize,
#     STOPWORDS,
    to_csv,
    tokenizer,
    words
)

# from Workflow import (
#     partition_dataset
# )



#KEYS = ('Question', 'Topic', 'Correct', 'Predicted', 'Gold')
RATIO_TEST_DATA = 0.4
RATIO_SPECIFICTY = 1.0
RATIO_CONFIDENCE = 0.9
EXPERIMENTS = 40


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
        return [w for p, w in prob_words[-int(len(prob_words) * RATIO_SPECIFICTY):]]



if __name__ == '__main__':

    results = []
    for e in range(1, EXPERIMENTS + 1):

        dataset = Dataset(
            '/Users/jordi/Laboratorio/corpora/anotados/Microsoft-WikiQA-corpus/WikiQACorpus/WikiQA.tsv'
            )
        dataset.load()


        #    first task
        invprob = InverseProbabilities(dataset)
        index = Index(invprob)

        train = [
    #         (bow(label, prob_filter=invprob) + bow(text, prob_filter=invprob), label, mark)
            (bow(text, prob_filter=invprob), label, mark)
            for text, label, mark in dataset.train()
        ]

        test = [
    #         (bow(label, prob_filter=invprob), label, mark)
            (bow(text, prob_filter=invprob), label, mark)
            for text, label, mark in dataset.test()
            if mark
        ][:int(len(train) * RATIO_TEST_DATA)]

        test += [
    #         (bow(label, prob_filter=invprob), label, mark)
            (bow(text, prob_filter=invprob), label, mark)
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

            if ratio <= RATIO_CONFIDENCE:
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
                f = f1(prec, rec)
            else:
                prec, rec, f = 0.0, 0.0, 0.0

            vector = (e, tp, tn, fp, fn, prec, rec, f)
            results.append(vector)

#             print label
#             print words(label)
#             print expectation
#             for x in matches[:5]:
#                 print '\t', x[0] / expectation, x
#             print 'tp: %d, tn: %d, fp: %d, fn: %d, all: %d, prec: %.2f, rec: %.2f, f1: %.2f' % (tp, tn, fp, fn, sum([tp, tn, fp, fn]), prec, rec, f)
#             print

        print '%d, tp: %d, tn: %d, fp: %d, fn: %d, all: %d, prec: %.2f, rec: %.2f, f1: %.2f' % (e, tp, tn, fp, fn, sum([tp, tn, fp, fn]), prec, rec, f)
        precs, recs, fs = zip(*results)[-3:]
        print e, avg(precs), avg(recs), avg(fs)
        print '---'

