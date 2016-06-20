import json

from Classifier import Classifier
from Dataset import Dataset
from FeatureEngine import FeatureEngine



if __name__ == '__main__':

    dataset = Dataset(
        '/Users/jordi/Laboratorio/corpora/anotados/Microsoft-WikiQA-corpus/WikiQACorpus/WikiQA.tsv'
        )
    dataset.load()

    fe = FeatureEngine()
    cls = Classifier()
    test, train = [], []
    for i, topic in enumerate(dataset):
        print json.dumps(topic, indent=4)

        for instance in topic['context']:
            triple = (' '.join(fe(instance['answer'])), topic['topic'], None)
            train.append(triple)

        for instance in topic['data']:
            triple = (' '.join(fe(instance['answer'])), topic['topic'], None)
            test.append(triple)

        print i
        print

    cls.train(train)
    for i, guess in enumerate(cls.test(test)):
        print test[i]
        print guess[:5]
        print
