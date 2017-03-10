import json, sys
from collections import defaultdict
import numpy as np
from gensim import corpora
from tabulate import tabulate
import unicodedata
################################################################################

with open("chennai_osm_raw_unique_names.json") as f:
#with open("_Data/louisiana_osm_raw_unique_names.json") as f:
    geo_locations = json.load(f)

################################################################################

lns = [x for x in geo_locations]
lns = [ unicodedata.normalize('NFKD', ln).encode('ascii','ignore') for ln in lns]
lns = [ln.strip() for ln in lns]
lns = [x for x in lns if ln != ""]

################################################################################

from sklearn.feature_extraction.text import TfidfVectorizer

tokenize = lambda doc: doc.lower().split(" ")

sklearn_tfidf = TfidfVectorizer(norm='l2',min_df=0, use_idf=True, smooth_idf=False, sublinear_tf=True, tokenizer=tokenize)
sklearn_representation = sklearn_tfidf.fit_transform(lns)


import lists

unnamed_lns_tfidfs = list()
lns_tfidf = list()

ln_to_tfidf_mapping = defaultdict(defaultdict)

for doc in range(len(lns)):
    feature_names = sklearn_tfidf.get_feature_names()
    feature_index = sklearn_representation[doc,:].nonzero()[1]
    tfidf_scores = zip(feature_index, [sklearn_representation[doc, x] for x in feature_index])

    words = list()
    tfidf = list()

    for w, s in [(feature_names[i], s) for (i, s) in tfidf_scores]:

        words.append(w)
        tfidf.append(s)

        ln_to_tfidf_mapping[doc][w] = s

        if w in lists.combined:
            unnamed_lns_tfidfs.append(s)

    lns_tfidf.append([words, tfidf])

avg_tfidf = np.mean(unnamed_lns_tfidfs)

header = ["Original LN", "Augmented LN"]

rows = list()

for idx, x in enumerate(lns):
    tokens = x.split()

    core = list()

    for token in tokens:
        if ln_to_tfidf_mapping[idx][token] > avg_tfidf:
            core.append(token)

    rows.append([x, " ".join(core)])

f = open('tfidf_based_output.txt', 'w')
f.write(tabulate(rows, headers=header, tablefmt="grid"))
f.close()
