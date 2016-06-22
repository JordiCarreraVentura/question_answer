import json


def partition_dataset(dataset, feature_engine, min_ctxt=5, n_macros=300):
    fe = feature_engine
    test, train = [], []
    for i, topic in enumerate(dataset):
#         print json.dumps(topic, indent=4)

        #	skip if the current topic has fewer than min_ctxt answers
        #	to use as training to detect that topic:
        if len(topic['context']) < min_ctxt:
            continue

        #	collect training instance (answer):
        for instance in topic['context']:
            a = instance['answer']
            triple = (
                ' '.join(fe(a)),
                topic['topic'],
                a
            )
            train.append(triple)

        #	collect test instance (question):
        for instance in topic['data'][:1]:
#             q = instance['answer']
            q = instance['question']
            triple = (
                ' '.join(fe(q)),
                topic['topic'],
                q
            )
            test.append(triple)

        #	terminate after iterating over n_macros templates:
        print i, n_macros
        if i >= n_macros:
            break
    
    return train, test
