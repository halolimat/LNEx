"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

# This model was inspired by the following sources:
# > http://www.katrinerk.com/courses/python-worksheets/language-models-in-python
# > http://stackoverflow.com/questions/21891247

################################################################################

from itertools import chain
from collections import defaultdict

import nltk
from nltk.util import bigrams, trigrams
from nltk.probability import ConditionalFreqDist
from nltk.probability import ConditionalProbDist

################################################################################
################################################################################

__all__ = [ 'GazBasedModel']

################################################################################

class GazBasedModel(object):
    '''The implementation of the language model using NLTK.'''

    def _bigram_probability(self, n_gram):
        '''Returns the probability of bigrams using the following equation:

            p (w_1 w_2) = p (w1) x p(w2 | w_1) '''


        # p(w_0)
        prob = (self.unigrams["words"][n_gram[0]] /
                float(self.unigrams["words_count"]))

        if len(n_gram) == 2:

            t1 = n_gram[0]
            t2 = n_gram[1]

            # p(w_1 | w_0)
            prob *= self.cpd_bigrams[t1].prob(t2)

        return prob

    ############################################################################

    def phrase_probability(self, phrase):
        '''Returns the probability of a phrase using the following equation:

            p (w_1 ... w_n) = p (w1) x p(w2 | w_1) ... x p (w_n | w_n-1) '''


        n_gram = phrase.split()
        n_gram = [t.strip() for t in n_gram]

        # tri or larger than trigrams will fall to tri
        if len(n_gram) > 2:

            # this will take care of p(w_0) * p(w_1|w_0)
            prob = self._bigram_probability(n_gram[:2])

            # calculate the probabilities where n > 3
            for __x in range(2, len(n_gram)):

                # I went home > t12 = I went , t3 = home
                t12 = " ".join(n_gram[__x - 2:__x])
                t3 = n_gram[__x]

                # p(w_i | w_i-2 w_i-1)
                prob *= self.cpd_trigrams[t12].prob(t3)

            return prob

        # probability of unigrams and bigrams
        elif len(n_gram) <= 2:

            return self._bigram_probability(n_gram)

    ############################################################################

    def __init__(self, geo_locations):
        '''Initializes the language model by creating the ConditionalFreqDist
        and ConditionalProbDist'''

        words_count = 0

        # will contain all names in a list which preserves their frequenceis as
        # they appear in the gazetteer. The frequenceis are going to be used in
        # the language model.
        gaz_n_grams = list()

        self.unigrams = defaultdict(int)

        for ln in geo_locations:

            number_of_mentions = len(geo_locations[ln])

            n_gram = ln.split()

            new_list = [n_gram] * number_of_mentions

            gaz_n_grams.extend(new_list)

            for token in n_gram:
                words_count += 1
                self.unigrams[token] += 1

        self.unigrams = {"words": self.unigrams, "words_count": words_count}

        # bigrams +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        train_bigrams = list(chain(*[bigrams(i) for i in gaz_n_grams]))

        cfd_bigrams = ConditionalFreqDist()

        for bg in train_bigrams:
            cfd_bigrams[bg[0]][bg[1]] += 1

        # bigrams MLE probabilities
        self.cpd_bigrams = ConditionalProbDist(cfd_bigrams, nltk.MLEProbDist)

        # trigrams ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        train_trigrams = list(chain(*[trigrams(i) for i in gaz_n_grams]))

        cfd_trigrams = ConditionalFreqDist()

        for bg in train_trigrams:

            bi_gr = " ".join(bg[:-1])

            cfd_trigrams[bi_gr][bg[2]] += 1

        # trigrams MLE probabilities
        self.cpd_trigrams = ConditionalProbDist(cfd_trigrams, nltk.MLEProbDist)

################################################################################

if __name__ == "__main__":

    import os
    import json

    data_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'data',
            'chennai_geo_locations.json'))

    with open(data_file) as f:
        geo_locations = json.load(f)

    lm = GazBasedModel(geo_locations)

    print(lm.phrase_probability("new"))

    lm.phrase_probability("new avadi")
    lm.phrase_probability("new avadi road")
    lm.phrase_probability("party of india")
    lm.phrase_probability("srm university")
    lm.phrase_probability("puram main road sabari")
