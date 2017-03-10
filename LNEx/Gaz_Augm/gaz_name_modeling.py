import json, sys
from collections import defaultdict
import numpy as np
from gensim import corpora
from tabulate import tabulate
import unicodedata
################################################################################

with open("_Data/chennai_osm_raw_unique_names.json") as f:
#with open("_Data/louisiana_osm_raw_unique_names.json") as f:
    geo_locations = json.load(f)

################################################################################

# create dictionary from location names

N = list()

#geo_locations = ["starbucks cafe", "peets cafe", "starbucks"]

for ln in geo_locations:

    ln = unicodedata.normalize('NFKD', ln).encode('ascii','ignore')

    splits = ln.split()

    if len(splits) == 0:
        continue

    N.append(splits)

id2token = corpora.Dictionary(N)

W_len = len(id2token.keys())

N_len = len(N)

################################################################################

z = defaultdict(defaultdict)

words_count = 0

# init-z
for n_nbr, n in enumerate(N):

    length = len(n)

    if length > 4:
        continue

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

            '''if z[w][n_nbr] > 0:
                z[w][n_nbr] = 1
            else:
                z[w][n_nbr] = 0'''

            c[w] = sum([z[w][p_of_w_in_n] for p_of_w_in_n in z[w]])/float(N_len)

            b[w] = sum([1-z[w][p_of_w_in_n] for p_of_w_in_n in z[w]])/float(words_count-N_len)

        except:
            # convergense of some terms... causes division by zero exception
            pass

#################

header = ["Original LN", "Augmented LN"]

rows = list()

for n_nbr, n in enumerate(N):

    l = list()

    for w in n:
        if c[w] > b[w]:
            l.append(1)
        else:
            l.append(0)

    b_arr = np.array([b[w] for w in n])
    c_arr = [c[w] for w in n]

    #######

    if sum(l) == 0:

        c_idx = np.where(b_arr == b_arr.min())

        core = [n[i] for i in np.nditer(c_idx)]

        rows.append([" ".join(n), " ".join(core)])

    else:

        l_arr = np.array(l)
        l_idx = np.where(l_arr == 1)

        core = [n[i] for i in np.nditer(l_idx)]

        rows.append([" ".join(n), " ".join(core)])

f = open('output.txt', 'w')
f.write(tabulate(rows, headers=header, tablefmt="grid"))
f.close()
