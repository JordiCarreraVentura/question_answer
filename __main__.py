
from copy import deepcopy as cp

from FeatureEngine import FeatureEngine

from FirstTask import (
    runner as first_task
)

from SecondTask import (
    runner as second_task
)

from Tools import to_csv


RESULTS_KEYS = [('Setting', 'Run #', 'TruePositives', 'TrueNegatives', 'FalsePositives',
                'FalseNegatives', 'Precision', 'Recall', 'F-1_Measure', 'Duration')]
# RATIO_TEST_DATA = 0.4
# RATIO_CONFIDENCE = 0.9
RATIO_SPECIFICITY = 1.0
EXPERIMENTS = 40
PATH_DATA = '/Users/jordi/Laboratorio/corpora/anotados/Microsoft-WikiQA-corpus/WikiQACorpus/WikiQA.tsv'

PARAMETERS = ['grams', 'chgrams', 'sgrams', 'test_n', 'r_conf']

PARAMETER_GRAMS = [
    ('off', []),
    ('uni', [1]),
    ('uni-bi-tri', [1, 2, 3])
]

PARAMETER_CHGRAMS = [
    ('off', []),
    ('on', [3, 4, 5])
]

PARAMETER_SKIPGRAMS = [
    ('off', []),
    ('on', [3, 4])
]

PARAMETER_TEST_DATA = [
#     ('0.1', 0.1),
    ('0.2', 0.2),
    ('0.4', 0.4)
]

PARAMETER_RATIO_CONFIDENCE = [
    ('0.5', 0.5),
#     ('0.8', 0.8),
    ('0.9', 0.9)
]


def discard_nograms(settings):
    new = []
    pars = ['grams', 'chgrams', 'sgrams']
    for setting in settings:
        if set([setting[par]['text'] for par in pars]) == set(['off']):
            continue
        else:
            new.append(setting)
    return new


if __name__ == '__main__':

    #	generate experimental settings:
    settings = [dict([])]
    for name, parameter in [
        ('grams', PARAMETER_GRAMS),
        ('chgrams', PARAMETER_CHGRAMS),
        ('sgrams', PARAMETER_SKIPGRAMS),
        ('test_n', PARAMETER_TEST_DATA),
        ('r_conf', PARAMETER_RATIO_CONFIDENCE)
    ]:
        new = []
        for setting in settings:
            for state_name, state_value in parameter:
                _new = cp(setting)
                _new[name] = {
                    'data': state_value,
                    'text': state_name
                }
                new.append(_new)
                #print [x['data'] for x in _new.values()]
        settings = new
    settings = discard_nograms(new)

    #	run all experiments with settings:
    results_first, results_second = [], []
    for setting in settings:

        setting_name = '.'.join(
            ['%s=%s' % (par, setting[par]['text'])
            for par in PARAMETERS]
        )

        fe = FeatureEngine(
            ngrams=setting['grams']['data'],
            ch_ngrams=setting['chgrams']['data'],
            skip_ngrams=setting['sgrams']['data']
        )

        _results = first_task(
            PATH_DATA,
            setting['test_n']['data'],
            RATIO_SPECIFICITY,
            setting['r_conf']['data'],
            EXPERIMENTS,
            fe,
            setting_name
        )

        if _results:
            results_first.append(tuple([setting_name] + list(_results)))

        _results = second_task(
            PATH_DATA,
            setting['test_n']['data'],
            RATIO_SPECIFICITY,
            setting['r_conf']['data'],
            EXPERIMENTS,
            fe,
            setting_name
        )

        if _results:
            results_second.append(tuple([setting_name] + list(_results)))


    to_csv(
        RESULTS_KEYS + sorted(results_first, key=lambda x: x[-2], reverse=True),
        'results.first_task.csv'
    )

    to_csv(
        RESULTS_KEYS + sorted(results_second, key=lambda x: x[-2], reverse=True),
        'results.second_task.csv'
    )
