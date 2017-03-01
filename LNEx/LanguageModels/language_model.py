# idea source: http://www.katrinerk.com/courses/python-worksheets/language-models-in-python
#http://stackoverflow.com/questions/21891247/how-to-append-values-to-generator-while-using-bigrams-in-conditionalfreqdist-met


import nltk
from nltk.util import bigrams, trigrams
from nltk.probability import ConditionalFreqDist, ConditionalProbDist

import operator
import sys, json, re, os
from itertools import chain
from collections import defaultdict, OrderedDict


class LanguageModel:

    def split_string(self, x):
        strings = x.split(",")
        strings = [item.split("-") for item in strings]

        return strings

    def bigram_probabilities(self, terms):

        # p(0)
        prob = (self.unigrams["words"][terms[0]]/
                    float(self.unigrams["words_count"]))

        for x in range(1, len(terms)):

            t1 = terms[x-1]
            t2 = terms[x]

            prob *= self.cpd[t1].prob(t2)

        return prob

    # noun phrase probability
    def np_prob(self, np):

        terms = np.split()
        terms = [t.strip() for t in terms]

        # tri or larger than trigrams will fall to tri to smooth it
        if len(terms) > 2:

            # this will take care of p(0) * p(1|0)
            prob = self.bigram_probabilities(terms[:2])

            # p(2:0&1) ... p(last token : previous 2)
            for x in range(2, len(terms)):

                # I went home > t12 = I went , t3 = home
                t12 = " ".join(terms[x-2:x])
                t3 = terms[x]

                prob *= self.cpd_trigrams[t12].prob(t3)

                #print t12, t3

            return prob

        # probability of bi and unigrams
        elif len(terms) <= 2:

            return self.bigram_probabilities(terms)


    def __init__(self, data):

        self.unigrams = defaultdict(int)

        osm_text = list()

        words_count = 0

        for loc_name in data:

            loc_name = loc_name.split()

            osm_text.append(loc_name)

            for token in loc_name:
                words_count += 1
                self.unigrams[token] += 1


        self.unigrams = { "words" : self.unigrams, "words_count" : words_count}

        # bigrams
        train_bigrams = list(chain(*[bigrams(i) for i in osm_text]))

        cfd = ConditionalFreqDist()

        for bg in train_bigrams:
            #cfd[bg[0]].inc(bg[1])
            cfd[bg[0]][bg[1]] += 1


        # Or if you prefer a one-liner.
        #cfd = ConditionalFreqDist((bg[0],bg[1]) for bg in list(chain(*[bigrams(i) for i in osm_text])))

        # trigrams
        train_trigrams = list(chain(*[trigrams(i) for i in osm_text]))

        cfd_trigrams = ConditionalFreqDist()

        for bg in train_trigrams:

            bi_gr = " ".join(bg[:-1])

            #print ">>", bi_gr, ">>>", bg[2]

            cfd_trigrams[bi_gr][bg[2]] += 1


        self.cpd = nltk.ConditionalProbDist(cfd, nltk.MLEProbDist)

        #trigrams probabilities
        self.cpd_trigrams = nltk.ConditionalProbDist(cfd_trigrams, nltk.MLEProbDist)


def get_data_dir():

    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    list_dir = dir_path.split(os.path.sep)
    idx_tmp = list_dir.index("DataProcessing")

    data_dir = os.path.sep + os.path.sep.join(list_dir[1:idx_tmp]) + \
                os.path.sep + "Data" + os.path.sep

    return data_dir


if __name__ == "__main__":

    data_file = get_data_dir()+"CombinedAugmentedGazetteers/chennai_language_model_osm_all_names_augmented.json"

    lm = LanguageModel(data_file)

    print lm.np_prob("puram main road sabari")

    sys.exit()

    print lm.np_prob("party of india")

    print lm.np_prob("new avadi road")

    print lm.np_prob("srm university")

    #NOTE: using only bigram cause the following problem:
    '''
    in west tambaram > in west is legal | west tambaram is legal then the
    combination is legal by the language model which is not true due to the
    smoothing.

    now. to solve this we used trigrams. and smooth for more than 3

    example smoothing problem: puram main road sabari.. the full is not legal
    but the 3grams are legal of the full text
    '''

    # problem of only 3 grams
    print lm.np_prob("puram main road sabari")
