import json, sys
from collections import defaultdict

from gensim import corpora

################################################################################

with open("_Data/louisiana_osm_raw_unique_names.json") as f:
    geo_locations = json.load(f)

################################################################################

# create dictionary from location names

N = list()

#geo_locations = ["starbucks cafe", "peets cafe", "starbucks"]

for ln in geo_locations:
    N.append(ln.split())

id2token = corpora.Dictionary(N)

W_len = len(id2token.keys())

N_len = len(N)

################################################################################

z = defaultdict(defaultdict)

words_count = 0

# init-z
for n_nbr, n in enumerate(N):

    length = len(n)
    words_count += length

    # filling out the uniformal distribution over all location names
    for idx, token in enumerate(n):
        z[token][n_nbr] = 1/float(length)

################################################################################

# init c and b

c = defaultdict()
b = defaultdict()

for n_nbr, n in enumerate(N):
    for w in n:
        c[w] = sum([z[w][p_of_w_in_n] for p_of_w_in_n in z[w]])/N_len

        b[w] = sum([1-z[w][p_of_w_in_n] for p_of_w_in_n in z[w]])/float(words_count-N_len)


################################################################################

# start Algorithm-1

for n_nbr, n in enumerate(N):

    for w in n:
        # for each word in a location name do:

        try:

            z[w][n_nbr] = (c[w]/float(b[w]))/float(sum([c[w_1]/float(b[w_1]) for w_1 in n]))

            c[w] = sum([z[w][p_of_w_in_n] for p_of_w_in_n in z[w]])/float(N_len)

            b[w] = sum([1-z[w][p_of_w_in_n] for p_of_w_in_n in z[w]])/float(words_count-N_len)

        except:
            # convergense of some terms... causes division by zero exception
            pass


for n_nbr, n in enumerate(N):

    l = list()

    for w in n:
        if c[w] > b[w]:
            l.append(1)
        else:
            l.append(0)

    print n, l, [c[w] for w in n], [b[w] for w in n]
