# -*- encoding: utf-8 -*-
import csv
import json
import nltk
import os
import re

from collections import (
    Counter,
    defaultdict as deft
)

from nltk import ngrams

from nltk.corpus import stopwords


STOPWORDS = {
    'es': stopwords.words('spanish'),
    'en': stopwords.words('english')
}


CHARS = [
    'á a',
    'é e',
    'í i',
    'ó o',
    'ú u',
    'ñ n'
]
CHARS = [tuple(x.decode('utf-8').split()) for x in CHARS]
VOWELS = re.compile('[aeiouáéíóú]'.decode('utf-8'))

LETTERS = re.compile('[a-z]+')
NUMBERS = re.compile('[0-9]+')
BLANK_COLON = re.compile(' :')
PARENTHESIS_COLON = re.compile(':[^a-z]*\(')

BRACKETS = re.compile('[\{\}]')

COMMA = re.compile(',')

PUNCT = re.compile('[\(\):;,\.\?! ]')
UNDERSCORE = re.compile('_')
METAPUNCT = re.compile('PUNCT')
BLANKS = re.compile(' {2,}')


def unicode2ascii(string):
    s = ''
    for char in string:
        norm = False
        for x, y in CHARS:
            if x == char:
                s += y
                norm = True
                break
        if not norm:
            s += char
    return s


def decode(item):
    if isinstance(item, list) or isinstance(item, tuple):
        return [decode(subitem) for subitem in item]
    else:
        try:
            return item.decode('utf-8')
        except Exception:
            return item


def encode(item):
    if isinstance(item, list) or isinstance(item, tuple):
        return [encode(subitem) for subitem in item]
    else:
        try:
            return item.encode('utf-8')
        except Exception:
            return item


def from_csv(path, delimiter=None):
    rows = []
    d = decode
    with open(path, 'rb') as rd:
        if delimiter:
            rdr = csv.reader(rd, delimiter=delimiter)
        else:
            rdr = csv.reader(rd)
        for row in rdr:
            rows.append(d(row))
    return rows


def to_csv(rows, out, delimiter=','):
    with open(out, 'wb') as wrt:
        wrtr = csv.writer(wrt, quoting=csv.QUOTE_MINIMAL, delimiter=delimiter)
        for row in rows:
            wrtr.writerow(encode(row))


def add_token(tokens, token, alnum):
    if not token:
        return
    if alnum and (token.isdigit() or token.isalpha()) or \
    not alnum and (LETTERS.search(token) or NUMBERS.search(token)):
        tokens.append(token)
    else:
        tokens.append('PUNCT')


def tokenizer(string, alnum=True):
    tokens = []
    token = ''
    for i, char in enumerate(string):
#         print i, char, tokens, token
        if char == ' ':
            add_token(tokens, token, alnum)
            token = ''
        elif alnum:
            if char.isalpha() and token.isalpha():
                token += char
            elif char.isalpha() and not token.isalpha():
                add_token(tokens, token, alnum)
                token = char
            elif char.isdigit() and token.isdigit():
                token += char
            elif token.isalpha():
                add_token(tokens, token, alnum)
                token = char
        elif not alnum and (char.isdigit() or char.isalpha()):
            token += char
        elif not alnum:
            add_token(tokens, token, alnum)
            token = ''
        else:
            add_token(tokens, token, alnum)
            token = char
    if token:
        add_token(tokens, token, alnum)
    return tokens


def normalize(string):
    return unicode2ascii(string.strip().lower())


stopwords = deft(bool)
for w in STOPWORDS['en']:
    stopwords[w] = True


def words(text):
    tokens = [w for w in tokenizer(text.lower()) if w != 'PUNCT']
#     return tokens
    return [w for w in tokens if not stopwords[w]]


def f1(prec, recall):
    return (2 * prec * recall) / (prec + recall)


def average(values):
    return sum(values) / len(values)


def bow(fe, text, ratio, prob_filter=None):
    if not prob_filter:
#         return fe(' '.join(words(text)))
        return words(text)
    else:
        prob_words = sorted([(prob_filter[w], w) for w in words(text)])
        return fe(' '.join([w for p, w in prob_words[-int(len(prob_words) * ratio):]]))
#         return [w for p, w in prob_words[-int(len(prob_words) * ratio):]]


def rounding(f):
    if isinstance(f, int):
        return f
    else:
        return round(f, 4)


def columns(results):
    if not results:
        return []
    cols = []
    for i in range(1, len(results[0])):
        col = [row[i] for row in results]
        cols.append(col)
    return cols


def create_folder(path):
    parts = path.split('/')
    curr = []
    while parts:
        curr.append(parts.pop(0))
        name = '/'.join(curr)
        if not os.path.exists(name):
            os.mkdir(name)
