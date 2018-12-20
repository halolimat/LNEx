"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

import re, os
import unicodedata
from itertools import groupby
from operator import itemgetter
from collections import defaultdict

################################################################################
################################################################################

__all__ = [ 'get_dicts_dir',
            'extract_all_bracketed_names',
            'Stack',
            'preprocess_name',
            'find_ngrams',
            'get_extended_words3',
            'filter_geo_locations',
            'augment']

################################################################################

def get_dicts_dir():
    '''Returns the directory where the to be used dictionaries resides'''

    return os.path.join(os.path.dirname(os.path.realpath(__file__)),
            '_Dictionaries/')

################################################################################

# will help in filtering out unigram location names
gaz_stopwords = get_dicts_dir() + "gaz_stopwords.txt"
gaz_stopwords = set([line.strip() for line in open(gaz_stopwords, 'r')])

################################################################################

def extract_all_bracketed_names(loc_name):
    '''Extracts the text inside brackets, with all the accompanied complexities
    The function does the job, developed while researching the problem...
    You know what I mean!'''

    final_list = list()
    final_list.append(loc_name)

    bracketed_names = list()

    sub_loc_name = loc_name

    # get all nested cracketed names
    while True:

        try:
            start_idx = sub_loc_name.index("(") + 1
            end_idx = sub_loc_name.rfind(")")

            sub_loc_name = sub_loc_name[start_idx:end_idx]

            bracketed_names.append(sub_loc_name)

            final_list.append(sub_loc_name)

        except BaseException:
            break

    bracketed_names = sorted(bracketed_names, key=len)

    for name in bracketed_names:

        loc_name = loc_name.replace(name, "").replace("()", "")
        loc_name = re.sub('\s{2,}', ' ', loc_name)

        final_list.append(loc_name)

    final_list = list(set(final_list))

    for idx, item  in enumerate(final_list):
        for j in range(idx, len(final_list)):

            sub_bracketed_name = "(" + item + ")"

            if sub_bracketed_name in final_list[j]:
                final_list.append(
                    final_list[j].replace(
                        sub_bracketed_name, ""))

    for idx, item in enumerate(final_list):
        item = item.replace("(", "").replace(")", "")
        item = re.sub('\s{2,}', ' ', item)
        item = item.strip()

    final_list = list(set(final_list))

    return final_list

################################################################################

class Stack(object):
    '''Stack data structure'''

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def isEmpty(self):
        return self.items == []

################################################################################

def preprocess_name(loc_name):
    '''Preprocesses and normalizes the raw location names. Including the
    implementation of the hand crafted rules of breaking'''

    loc_name = loc_name.lower()

    # expand and break name

    list_of_separators = [",", "/", ";"]

    # names between brackets as new names ##########################
    brackets_name = extract_all_bracketed_names(loc_name)

    # create stack to hold all bracketed names
    to_break = Stack()

    for b_name in brackets_name:
        to_break.push(b_name)

    # start splitting names on separators
    final_list = list()

    while not to_break.isEmpty():

        name_to_break = to_break.pop()

        separators = set(list(name_to_break)) & set(list_of_separators)

        if separators:
            for sep in separators:
                broken = name_to_break.split(sep)

                both_pieces = name_to_break.replace(sep, "")

                to_break.push(both_pieces)

                for b in broken:
                    to_break.push(b)

        else:
            sep = " - "

            if sep in name_to_break:
                broken = name_to_break.split(sep)

                both_pieces = name_to_break.replace(sep, " ")

                to_break.push(both_pieces)

                for b in broken:
                    to_break.push(b)

            else:
                final_list.append(name_to_break)

    for __, item in enumerate(final_list):

        # to remove all punctuations from the tweet later
        # and since it is not important if it is there or not
        # for matching, so we just remove it. If not removed
        # then both terms connected will be considered as a
        # unigram which is not true.
        if "-" in item:
            item = item.replace("-", " ")

        item = re.sub('\s{2,}', ' ', item)
        item = item.strip()

    final_list = list(set(final_list))

    return final_list

################################################################################

def find_ngrams(unigrams, n):
    '''Created ngrams of length n from the unigrams list'''

    return list(zip(*[unigrams[i:] for i in range(n)]))

################################################################################

def get_extended_words3(unique_names):
    '''Reads the list of english words (words3).
    words3 source: https://github.com/dwyl/english-words
    '''

    with open(get_dicts_dir() + "words3.txt") as f:

        words3 = f.read().splitlines()
        words3 = [x.lower() for x in words3]
        words3 = set(words3)

    # extend the list of words
    for x in unique_names:

        for y in x.split():
            if y not in words3:

                words3.add(y)

    return list(words3)

################################################################################

def high_precision_filtering(geo_locations):
    ''' High Precision Filtering of location names.

    input>  type(geo_locations): defaultdict
            "LocationName": [geo_info_ids]

    output> type(unique_names): dict , type(all_names): list'''

    new_geo_locations = defaultdict(lambda: defaultdict(set))

    for text in geo_locations:

        original_text = text

        text = text.replace("( ", "(").replace(" )", ")").lower()

        # punctuation padding
        text = re.sub('([,;])', r'\1 ', text)
        text = re.sub('\s{2,}', ' ', text)

        # remove the names in brackets
        start_idx = text.find("(") + 1
        end_idx = text.rfind(")")
        if start_idx > 0: text = text[:start_idx]+text[end_idx:]

        #break on seperators, keep only the first part
        text = text.split(",")[0]
        text = text.split("/")[0]
        text = text.split(";")[0]

        text = re.sub('\s{2,}', ' ', text).strip()

        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('UTF-8')
        text = str(text.strip())

        # skip few names
        if text == "" or text.isdigit() or text in gaz_stopwords or len(text) < 3:
            continue

        # prevents collisions
        if text not in new_geo_locations:
            new_geo_locations[text]["main"] = set(geo_locations[original_text]["main"]).union(new_geo_locations[text]["main"])
            new_geo_locations[text]["meta"] = set(geo_locations[original_text]["meta"]).union(new_geo_locations[text]["meta"])

    return new_geo_locations

################################################################################

def filter_geo_locations(geo_locations):
    ''' Filters out the gazetteer location names.

    input>  type(geo_locations): defaultdict
            "LocationName": [geo_info_ids]

    output> type(unique_names): dict , type(all_names): list'''


    names_to_remove = set(["(U/C)",
                           "(East)",
                           "(?)",
                           "(100 Feet Road)",
                           "(partialy closed for metro)",
                           "(North)",
                           "(planned)",
                           "(Broadway)",
                           "(planned)",
                           "(closed)",
                           "(P)",
                           "(Old)",
                           "(M)",
                           "(Primary)",
                           "(West)",
                           "(South)",
                           "(Big Street)",
                           "(A Comfort Stay)",
                           "(historical)",
                           "(Pvt)",
                           "(L31)",
                           "(MVN)",
                           "(Private Road)",
                           "(north.extn)",
                           "(2362 xxxx)",
                           "(current)",
                           "(leads)",
                           "(private use)",
                           "(heritage)",
                           "(rural)",
                           "(am)",
                           "(fm)",
                           "(tv)",
                           "(ship)",
                           "(u.s. season 2)",
                           "(boat)",
                           "(abandoned)",
                           "(part)"])

    names_to_remove = set([x.lower() for x in names_to_remove])

    ############################################################################

    new_geo_locations = defaultdict(lambda: defaultdict(set))

    # step 1 (Filtering) +++++++++++++++++++++++++++++++++++++++++++++++++++++

    for text in geo_locations:

        original_text = text

        text = text.replace("( ", "(").replace(" )", ")")

        text = text.lower()

        # remove bracketed blacklisted bracketed mentions
        for name_to_remove in names_to_remove:
            if name_to_remove in text:
                text = text.replace(name_to_remove, "")

        # punctuation padding
        text = re.sub('([,;])', r'\1 ', text)
        text = re.sub('\s{2,}', ' ', text)

        names = preprocess_name(text)

        ###################################

        for name in names:

            name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('UTF-8')
            name = str(name.strip())

            # skip empty names
            if name == "" or name.isdigit() or name in gaz_stopwords or len(name) < 3:
                continue

            # prevents collisions
            if name not in new_geo_locations:
                new_geo_locations[name]["main"] = set(geo_locations[original_text]["main"]).union(new_geo_locations[name]["main"])
                new_geo_locations[name]["meta"] = set(geo_locations[original_text]["meta"]).union(new_geo_locations[name]["meta"])

    return new_geo_locations

################################################################################

def augment(geo_locations):

    '''Augments the location names using skip grams'''

    # augmentation includes filtering
    new_geo_locations = filter_geo_locations(geo_locations)

    # step 2 (Augmentation) ++++++++++++++++++++++++++++++++++++++++++++++++++++

    # TODO: join the too
    list_tops_to_remove = [
        "a",
        "people",
        "closed",
        "planned",
        "me",
        "you",
        "us",
        "our",
        "ours",
        "their",
        "open",
        "opened",
        "restore",
        "plz",
        "rt",
        "live",
        "htt",
        "free",
        "chopper",
        "service",
        "entire",
        "west",
        "south",
        "east",
        "north",
        "frm",
        "wht",
        "old",
        "new",
        "helpline",
        "helplines",
        "welcome",
        "stuff",
        "uptodate",
        "more",
        "ahead",
        "5th",
        "id",
        "",
        "all",
        "is",
        "plans",
        "gulf",
        "white",
        "3rd",
        ""]

    lns = set(new_geo_locations)

    for name in lns:

        nospaces = name.replace(" ", "")

        if name not in list_tops_to_remove and len(
                nospaces) > 2 and not nospaces.isdigit():

            # remove all non-alphaneumeric characters
            alphanumeric_name = re.sub(r'\W+', ' ', name)
            alphanumeric_name = alphanumeric_name.strip()

            if alphanumeric_name != name and alphanumeric_name not in gaz_stopwords:

                # not in the list of names before augmentation
                if alphanumeric_name not in lns:

                    new_geo_locations[alphanumeric_name]["main"] = \
                        set(new_geo_locations[name]["main"]).union(new_geo_locations[alphanumeric_name]["main"])

                    new_geo_locations[alphanumeric_name]["meta"] = \
                        set(new_geo_locations[name]["meta"]).union(new_geo_locations[alphanumeric_name]["meta"])


    # step 3 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # create skip grams

    lns2 = set(new_geo_locations)

    for name in lns2:

        name_list = name.split()
        name_len = len(name_list)

        flexi_grams = list()

        if name_len > 2:
            flexi_gram = [name_list[0], name_list[name_len - 1]]

            # add grams with filling of size 0
            flexi_grams.append(" ".join(flexi_gram))

            filling_length = len(name_list[1:-1])

            # add flexi with filling of size 1 to len - 2
            for x in range(1, filling_length):

                filling_names = find_ngrams(name_list[1:-1], x)

                for f_name in filling_names:

                    base_name = list(flexi_gram)

                    base_name[1:1] = f_name

                    # remove consecutive duplicate tokens
                    base_name = list(map(itemgetter(0), groupby(base_name)))

                    flexi_grams.append(" ".join(base_name))

        for new_name in set(flexi_grams):

            nospaces = new_name.replace(" ", "")

            if len(nospaces) > 2 and not nospaces.isdigit():

                # don't add
                if new_name in gaz_stopwords:
                    continue

                # not in the list of names before augmentation
                if new_name not in lns:

                    new_geo_locations[new_name]["main"] = \
                        set(new_geo_locations[name]["main"]).union(new_geo_locations[new_name]["main"])

                    new_geo_locations[new_name]["meta"] = \
                        set(new_geo_locations[name]["meta"]).union(new_geo_locations[new_name]["meta"])

    return new_geo_locations, get_extended_words3(list(new_geo_locations.keys()))
