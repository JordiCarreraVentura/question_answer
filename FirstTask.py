
import time

from Dataset import Dataset

from collections import (
    Counter,
    defaultdict as deft
)

from Index import Index

from InverseProbabilities import InverseProbabilities

from QuestionTypes import QuestionTypes

from Tools import (
    average as avg,
    bow,
    columns,
    f1,
    normalize,
    rounding as _r,
    to_csv,
    tokenizer
)



RESULTS_KEYS = [
    ('Iteration', 'TruePositives', 'TrueNegatives',
     'FalsePositives', 'FalseNegatives',
     'Precision', 'Recall', 'F-1_Measure', 'Time')
    ]
ERROR_KEYS = ('Occurrences', 'ErrorType', 'Predicted', 'Expected')
RESULTS_FOLDER = 'results_testn0.2/first/'
RESULTS_FOLDER = 'results/first/'

def runner(
        PATH_DATA,
        RATIO_TEST_DATA,
        RATIO_SPECIFICITY,
        RATIO_CONFIDENCE,
        EXPERIMENTS,
        fe,
        setting_name
    ):

    results = []
    errors = Counter()
    qtypes = QuestionTypes()
    for e in range(1, EXPERIMENTS + 1):

        start = time.time()
        dataset = Dataset(PATH_DATA)
        dataset.load()

        invprob = InverseProbabilities(dataset)
        index = Index(invprob)

        train = [
    #         (bow(fe, label, RATIO_SPECIFICITY, prob_filter=invprob) + bow(fe, text, prob_filter=invprob), label, mark)
            (bow(fe, text, RATIO_SPECIFICITY, prob_filter=invprob), label, mark)
            for text, label, mark in dataset.train()
        ]
        train = train * 4

        test = [
    #         (bow(fe, label, RATIO_SPECIFICITY, prob_filter=invprob), label, mark)
            (bow(fe, text, RATIO_SPECIFICITY, prob_filter=invprob), label, mark)
            for text, label, mark in dataset.test()
            if mark
        ][:int(len(train) * RATIO_TEST_DATA)]

        test += [
    #         (bow(fe, label, RATIO_SPECIFICITY, prob_filter=invprob), label, mark)
            (bow(fe, text, RATIO_SPECIFICITY, prob_filter=invprob), label, mark)
            for text, label, mark in dataset.test()
            if not mark
        ][:len(test)]

        for tbow, label, mark in train:
            index.update(tbow)
            index.add(label)

        tp, tn, fp, fn = 0, 0, 0, 0
        marked = sum([1 for _, _, mark in test if mark])
        for tbow, label, mark in test:
            qtypes.increment(label)
            expectation = sum([
                invprob[w]
                for w in set(bow(fe, label, RATIO_SPECIFICITY, prob_filter=invprob))
            ])
            matches = index(tbow)

            if not matches and not mark:
                tn += 1
                continue
            elif not matches and mark:
                fn += 1
                errors[('fn', '', label)] += 1
                qtypes.update('fn', None, label)
                continue

            best_match = matches[0]
            guess = best_match[2]
            sim = best_match[0]
            ratio = sim / (expectation + 0.1)

            if ratio <= RATIO_CONFIDENCE:
                if not mark:
                    tn += 1
                    continue
                else:
                    fn += 1
                    errors[('fn', '', label)] += 1
                    qtypes.update('fn', None, label)
                    continue
            else:
                if mark and guess == label:
                    tp += 1
                elif mark:
                    fp += 1
                    _qtype = '_'.join(guess.lower().split()[:2])
                    errors[('fp', guess, label)] += 1
                    qtypes.update('fp', guess, label)

            duration = time.time() - start
            if tp:
                prec = tp / float(tp + fp)
                rec = tp / float(tp + fn)
                f = f1(prec, rec)
            else:
                prec, rec, f = 0.0, 0.0, 0.0

        vector = (e, _r(tp), _r(tn), _r(fp), _r(fn),
                  _r(prec), _r(rec), _r(f), _r(duration))
        results.append(vector)

        print '%d, tp: %d, tn: %d, fp: %d, fn: %d, all: %d, prec: %.2f, rec: %.2f, f1: %.2f, time=%.2f' % (e, tp, tn, fp, fn, sum([tp, tn, fp, fn]), prec, rec, f, duration)
        precs, recs, fs = zip(*results)[-4:-1]
        print e, avg(precs), avg(recs), avg(fs)
        print '---'

    if not results:
        return None

    cols = columns(results)
    columns_int = [avg(col) for col in cols[:4]]
    columns_float = [_r(avg(col)) for col in cols[4:]]
    summary_row = [
        tuple(['all'] + columns_int + columns_float)
    ]

    to_csv(
        RESULTS_KEYS + results + summary_row,
        '%sfirst_task.%s.results.csv' % (RESULTS_FOLDER, setting_name)
    )

    to_csv(
        [tuple([f] + list(key)) for key, f in errors.most_common()],
        '%sfirst_task.%s.errors.csv' % (RESULTS_FOLDER, setting_name)
    )

    to_csv(
        qtypes.dump(),
        '%sfirst_task.error.%s.question_types.csv' % (RESULTS_FOLDER, setting_name)
    )

    return summary_row[0]



