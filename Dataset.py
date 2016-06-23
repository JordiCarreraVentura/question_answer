import nltk

import random

from collections import (
    Counter,
    defaultdict as deft
)

# from nltk import sent_tokenize as splitter

from random import choice


class Dataset:


    def __init__(self, path):
        self.source = path
        self._train = []
        self._test = []


    def __get_records(self):
        records = []
        with open(self.source, 'rb') as rd:
            for line in rd:
                fields = line.decode('utf-8').strip().split('\t')
                if not fields[-1].isdigit():
                    continue
                records.append(fields)
        return records


    def __group_records(self, records):
        answers = deft(list)
        counts = Counter()
        for fields in records:
            score = int(fields[-1])
            topic = fields[3]
            question = fields[1]
            answer = fields[-2]

            if counts[question] == 2:
                continue

            if score:
                answers[question].append(answer)
                counts[question] += 1

        return answers


    def __partition_dataset(self, answers):
        for q, aa in answers.items():
            if len(aa) > 1:
                test_i = random.randint(0, len(aa) - 1)
                _a = aa[test_i]
                __a = aa[:test_i] + aa[test_i + 1:]
                self._train += [(answer, q, True) for answer in __a]
                self._test.append((_a, q, True))
            else:
                self._test.append((aa[0], q, False))


    def load(self):
        records = self.__get_records()
        answers = self.__group_records(records)
        self.__partition_dataset(answers)


    def train(self):
        for record in self._train:
            yield record


    def test(self):
        for record in self._test:
            yield record

