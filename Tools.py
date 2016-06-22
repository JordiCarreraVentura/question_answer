# -*- encoding: utf-8 -*-
import csv
import json
import nltk
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

HTML = re.compile('<[^>]+>')

SENT_SEPARATOR = re.compile('([\.!\?]).{,2}\n{1,}')

VERSIONS = re.compile('\-?([0-9]+\-[0-9]+).*$')

PUNCT = re.compile('[\(\):;,\.\?! ]')
UNDERSCORE = re.compile('_')
METAPUNCT = re.compile('PUNCT')
BLANKS = re.compile(' {2,}')


REGEX = [
    ('html', '"', 'quot', u'&quot;', False),
    ('html', '>', 'gt', u'&gt;', False),
    ('html', '<', 'lt', u'&lt;', False),
    ('html', '\'', 'apos', u'&apos;', False),
    ('html', '\'', 'amp_apos', u'&amp;apos;', False),
    ('html', '&', 'amp ', u'&amp; ?', False),
    ('html', '/', 'slash', u'&slash;', False)
]

EXPRESSIONS = deft(dict)
REPLACEMENTS = deft(dict)
for parser, replacement, name, regex, ignore in REGEX:
    if ignore:
        EXPRESSIONS[parser][name] = re.compile(regex, re.IGNORECASE)
    else:
        EXPRESSIONS[parser][name] = re.compile(regex)
    if replacement:
        REPLACEMENTS[parser][name] = replacement
E = EXPRESSIONS
R = REPLACEMENTS


def rm_html(string):
    return HTML.sub('', string)


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


def html_substitutions(text):
    for name, regex in E['html'].items():
        text = regex.sub(R['html'][name], text)
    return text


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


def grams(
    tokens,
    punct_break=True,
    nn=[
        (1, False),
        (2, False),
        (3, False),
        (4, False),
        (5, False)
    ],
    stopwords=None
):
    _grams = []
    for n, skip in nn:
        new_grams = list(ngrams(tokens, n))
        if punct_break:
            new_grams = [
                g for g in new_grams if 'PUNCT' not in g
            ]
        if stopwords and n > 1:
            new_grams = [
                g for g in new_grams if (
                    not stopwords[g[0]] and not stopwords[g[-1]]
                )
            ]
        _grams += [' '.join(list(g)) for g in new_grams]
    return _grams


def esdex2endex(string):
    return float(COMMA.sub('.', string))


def read_one(filepath):
    lines = []
    with open(filepath, 'rb') as rd:
        for line in rd:
            l = line.decode('utf-8').strip()
            if l:
               lines.append(l)
    return lines


def strong_encode(string):
    new = ''
    for char in string:
        try:
            char.encode('utf-8')
            new += char
        except Exception:
            pass
    return new



class GramIndex:
    
    def __init__(self, n=3):
        self.qq_by_g = deft(list)
        self.fx = Counter()
        self.mass = 0.0
        self.fxy = deft(Counter)
        self.masses = deft(float)
        self.n = 4
    
    def add(self, name):
        for g in self.grams(NUMBERS.sub('', name).strip()):
            self.qq_by_g[g].append(name)
            self.fx[g] += 1
            self.mass += 1
            self.masses[name] += 1
            self.fxy[name][g] += 1

    def grams(self, name):
        _grams = ngrams(name, self.n)
        if not _grams:
            return [name]
        return [''.join(g) for g in _grams]
    
    def build(self):
        for g, qq in self.qq_by_g.items():
            self.qq_by_g[g] = set(qq)
    
    def __call__(self, cname, limit=None, within=0.6):
        activated, activation = self.__activate(cname, limit)
        recomms = self.__choose(cname, limit, activated, activation, within)
        best = sorted(recomms, key=lambda x: x[1], reverse=True)[0][0]
        return best
    
    def __activate(self, name, limit):
        activated = deft(int)
        activation = deft(float)
        for g in self.grams(name):
            for q in self.qq_by_g[g]:
                if limit and len(q) > limit:
                    continue
                mi = self.mi(name, g)
                activation[q] += mi
                activated[q] += 1
        return activated, activation
    
    def __choose(self, cname, limit, activated, activation, within):
        actdist = sorted(activated.items(), key=lambda x: x[1], reverse=True)
        midist = sorted(activation.items(), key=lambda x: x[1], reverse=True)
        _, f = actdist[0]
        threshold_f = f * within
        space_f = [w for w, f in actdist if f >= threshold_f]
        space_mi = [(w, activation[w]) for w in space_f]
        return space_mi
    
    def mi(self, name, g):
        px = self.fx[g] / self.mass
        pxy = self.fxy[name][g] / self.masses[name]
        #return pxy * (pxy / px)
        return 1.0


def find_xf_in_doc(xf, doc):
    score = 0
    space = [x for x in xf]
    _q = ''.join([char for char in doc])
    while _q and space:
        w, f = space.pop(0)
        if w in _q:
            score += f
            _q = ' '.join(_q.split(' %s ' % w))
    return score


def doc2dotted(doc):
    while True:
        match = SENT_SEPARATOR.search(doc)
        if not match:
            return doc
        else:
            start, end = match.end(1), match.end()
            doc = doc[:start] + ' ' + doc[end:]
         

def rm_versions(string):
    return VERSIONS.sub('', string)


def restore_string(string):
    string = METAPUNCT.sub('', string)
    string = UNDERSCORE.sub(' ', string)
    string = BLANKS.sub(' ', string)
    return string


def postprocess(string):

    if not string:
        return string

    string = html_substitutions(string)
    string = PARENTHESIS_COLON.sub(':', string)
    string = BLANK_COLON.sub(':', string)
    string = trim_punct(string)
    string = capitalize_first_letter(string)

    if u'¡' in string and '!' not in string:
        string += '!'
    elif u'¿' in string and '?' not in string:
        string += '?'
    elif u'(' in string and ')' not in string:
        string += ')'

    return string


def trim_punct(string):
 
#     print
    for start, char in enumerate(string):
#         print start, char, string[start:]
        if not PUNCT.match(char):
            break

    end = len(string)
    for i in range(1, len(string) + 1):
#         print len(string) - (i - 1), char, string[:len(string) - (i - 1)]
        if PUNCT.match(string[-i]):
            end = len(string) - (i - 1)
        else:
            break
    
    return string[start:end]


def capitalize_first_letter(string):
    for i, char in enumerate(string):
        if char.isalpha() and not char.isupper():
            string = ''.join(string[:i]) + \
                     char.upper() + \
                     ''.join(string[i + 1:])
            return string
        elif char.isalpha() or char.isdigit():
            return string
    return string


def items2campaign(kws_by_url, generator):

    keys = ('Keyword', 'Adgroup', 'Headline', 'Description line 1', 'Description line 2', 'Display URL', 'Final URL', 'Match', 'Negative', 'Campaign name')
    rows = [keys]
    campaign = 'QRZ_%s_%s' % (generator.client, generator.lang)

    ad_copies = [('cluster_name', 'top-3-words', 'title', 'dl1', 'dl2', 'visible_url', 'landing_page')]
    for i, item in enumerate(generator):
    
        url = item['url']
        ad_copy = generator.ad_copy(url)
        kws = kws_by_url[url]

        ad_copies.append(
            (ad_copy['cluster_name'], ad_copy['ad_group'], ad_copy['title'],
             ad_copy['dl1'], ad_copy['dl2'], ad_copy['visible_url'], url)
        )

        for kw in kws:
            row = (kw, ad_copy['ad_group'], ad_copy['title'], ad_copy['dl1'],
                   ad_copy['dl2'], ad_copy['visible_url'],
                   url, 'MODIFIED', 0, campaign)
            rows.append(row)

        if not i % 5:
            print i, (ad_copy['cluster_name'], ad_copy['ad_group'], ad_copy['title'], ad_copy['dl1'], ad_copy['dl2'], ad_copy['visible_url'], url)
    
    filename = '%s.csv' % campaign
    to_csv(rows, filename, delimiter=';')
    to_csv(ad_copies, '%s.adcopies.csv' % campaign)


def recall(clustering):
    ad_groups = dict([])
    kws_by_url = deft(list)
    for row in clustering[1:]:
        rel = float(row[-1])
        kw = row[1]
        cname = row[4]
        if rel >= 0.8:
#         if rel >= 0.0:
            url = row[-3]
            kws_by_url[url].append(kw)
            ad_groups[url] = cname
    return ad_groups, kws_by_url


def json_print(data):
    print json.dumps(data, indent=4)


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
    return 2 * ((prec * recall) / (prec + recall))


def average(values):
    return sum(values) / len(values)
