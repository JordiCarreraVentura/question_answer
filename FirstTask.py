
from Dataset import Dataset

from collections import (
    Counter,
    defaultdict as deft
)

from Index import Index

from InverseProbabilities import InverseProbabilities

from Tools import (
    average as avg,
    bow,
    f1,
    normalize,
    to_csv,
    tokenizer
)


def runner(
        PATH_DATA,
        RATIO_TEST_DATA,
        RATIO_SPECIFICTY,
        RATIO_CONFIDENCE,
        EXPERIMENTS,
        fe
    ):

    results = []
    for e in range(1, EXPERIMENTS + 1):

        dataset = Dataset(PATH_DATA)
        dataset.load()

        invprob = InverseProbabilities(dataset)
        index = Index(invprob)

        train = [
    #         (bow(fe, label, RATIO_SPECIFICTY, prob_filter=invprob) + bow(fe, text, prob_filter=invprob), label, mark)
            (bow(fe, text, RATIO_SPECIFICTY, prob_filter=invprob), label, mark)
            for text, label, mark in dataset.train()
        ]

        test = [
    #         (bow(fe, label, RATIO_SPECIFICTY, prob_filter=invprob), label, mark)
            (bow(fe, text, RATIO_SPECIFICTY, prob_filter=invprob), label, mark)
            for text, label, mark in dataset.test()
            if mark
        ][:int(len(train) * RATIO_TEST_DATA)]

        test += [
    #         (bow(fe, label, RATIO_SPECIFICTY, prob_filter=invprob), label, mark)
            (bow(fe, text, RATIO_SPECIFICTY, prob_filter=invprob), label, mark)
            for text, label, mark in dataset.test()
            if not mark
        ][:len(test)]

        for tbow, label, mark in train:
            index.update(tbow)
            index.add(label)

        tp, tn, fp, fn = 0, 0, 0, 0
        marked = sum([1 for _, _, mark in test if mark])
        for tbow, label, mark in test:
            expectation = sum([
                invprob[w]
                for w in set(bow(fe, label, RATIO_SPECIFICTY, prob_filter=invprob))
            ])
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


