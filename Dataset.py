
from collections import (
    defaultdict as deft
)


class Dataset:


    def __init__(self, path):
        self.source = path
        self.templated = deft(list)
        self.context = deft(list)


    def load(self):
        with open(self.source, 'rb') as rd:
            for line in rd:
                fields = line.decode('utf-8').strip().split('\t')

                if not fields[-1].isdigit():
                    continue

                score = int(fields[-1])
                topic = fields[3]
                template = {
                    'question': fields[1],
                    'answer': fields[-2],
                }

                if score:
                    self.templated[topic].append(template)
                else:
                    self.context[topic].append(template)


    def __iter__(self):
        for topic, data in self.templated.items():
            if len(data) > 1:
                yield {
                    'topic': topic,
                    'data': data,
                    'context': self.context[topic],
                    'type': 'template'
                }
            else:
                yield {
                    'topic': topic,
                    'data': data,
                    'context': self.context[topic],
                    'type': 'negative_example'
                }

