
from FeatureEngine import FeatureEngine

from FirstTask import (
    runner as first_task
)

from SecondTask import (
    runner as second_task
)


#KEYS = ('Question', 'Topic', 'Correct', 'Predicted', 'Gold')
RATIO_TEST_DATA = 0.4
RATIO_SPECIFICITY = 1.0
RATIO_CONFIDENCE = 0.9
EXPERIMENTS = 4
PATH_DATA = '/Users/jordi/Laboratorio/corpora/anotados/Microsoft-WikiQA-corpus/WikiQACorpus/WikiQA.tsv'


if __name__ == '__main__':

    fe = FeatureEngine()

    first_task(
        PATH_DATA,
        RATIO_TEST_DATA,
        RATIO_SPECIFICITY,
        RATIO_CONFIDENCE,
        EXPERIMENTS,
        fe
    )
    
    second_task(
        PATH_DATA,
        RATIO_TEST_DATA,
        RATIO_SPECIFICITY,
        RATIO_CONFIDENCE,
        EXPERIMENTS,
        fe
    )

