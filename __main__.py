import json

from Dataset import Dataset


if __name__ == '__main__':

    dataset = Dataset(
        '/Users/jordi/Laboratorio/corpora/anotados/Microsoft-WikiQA-corpus/WikiQACorpus/WikiQA.tsv'
        )
    dataset.load()

    for topic in dataset:
        if len(topic['data']) > 1:
            print json.dumps(topic, indent=4)
            raw_input()
