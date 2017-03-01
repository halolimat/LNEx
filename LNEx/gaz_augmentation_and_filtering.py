import json, sys, os, re
from json import JSONEncoder
from itertools import groupby
from operator import itemgetter
from collections import defaultdict
import unicodedata


#TODO: refactor this crappy code
def extract_all_bracketed_names(loc_name):

    final_list = list()
    final_list.append(loc_name)

    bracketed_names = list()

    sub_loc_name = loc_name

    # get all nested cracketed names
    while True:

        try:
            start_idx = sub_loc_name.index("(")+1
            end_idx = sub_loc_name.rfind(")")

            sub_loc_name = sub_loc_name[start_idx:end_idx]

            bracketed_names.append(sub_loc_name)

            final_list.append(sub_loc_name)

        except:
            break

    bracketed_names = sorted(bracketed_names, key=len)

    for name in bracketed_names:

        loc_name = loc_name.replace(name, "").replace("()", "")
        loc_name = re.sub('\s{2,}', ' ', loc_name)

        final_list.append(loc_name)

    final_list = list(set(final_list))

    for i in range(len(final_list)):
        for j in range(i, len(final_list)):

            sub_bracketed_name = "("+final_list[i]+")"

            if sub_bracketed_name in final_list[j]:
                final_list.append(final_list[j].replace(sub_bracketed_name, ""))

    for i in range(len(final_list)):
        final_list[i] = final_list[i].replace("(", "").replace(")","")
        final_list[i] = re.sub('\s{2,}', ' ', final_list[i])
        final_list[i] = final_list[i].strip()

    final_list = list(set(final_list))

    return final_list

class Stack:
     def __init__(self):
         self.items = []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def isEmpty(self):
         return self.items == []


def preprocess_name(loc_name):

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

                both_pieces = name_to_break.replace(sep,"")

                to_break.push(both_pieces)

                for b in broken:
                    to_break.push(b)

        else:
            sep = " - "

            if sep in name_to_break:
                broken = name_to_break.split(sep)

                both_pieces = name_to_break.replace(sep," ")

                to_break.push(both_pieces)

                for b in broken:
                    to_break.push(b)

            else:
                final_list.append(name_to_break)


    for i in range(len(final_list)):

        # to remove all punctuations from the tweet later
        # and since it is not important if it is there or not
        # for matching, so we just remove it. If not removed
        # then both terms connected will be considered as a
        # unigram which is not true.
        if "-" in final_list[i]:
            final_list[i] = final_list[i].replace("-"," ")

        final_list[i] = re.sub('\s{2,}', ' ', final_list[i])
        final_list[i] = final_list[i].strip()

    final_list = list(set(final_list))

    return final_list


#source: http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
def find_ngrams(input_list, n):
  return zip(*[input_list[i:] for i in range(n)])


def get_extended_words3_list(unique_names):

    # words3 source: https://github.com/dwyl/english-words
    with open("Dictionaries/words3.txt") as f:

        words3 = f.read().splitlines()
        words3 = [x.lower() for x in words3]
        words3 = set(words3)

    # extend the list of words
    for x in unique_names:

        for y in x.split():
            if y not in words3:

                y = unicodedata.normalize('NFKD', y).encode('ascii','ignore')

                words3.add(y)

    return words3

def run(raw_names):
    """
    input>  type(raw_names): list
    output> type(unique_names): dict , type(all_names): list

    """

    names_to_remove = ["", "(?)", "(100 Feet Road)", "(2362 xxxx)", "(A Comfort Stay)", "(abandoned)", "(am)", "(Big Street)", "(boat)", "(Broadway)", "(closed)", "(current)", "(East)", "(fm)", "(heritage)", "(historical)", "(L31)", "(leads)", "(M)", "(MVN)", "(north.extn)", "(North)", "(Old)", "(P)", "(partialy closed for metro)", "(planned)", "(Primary)", "(Private Road)", "(private use)", "(Pvt)", "(rural)", "(ship)", "(South)", "(tv)", "(u.s. season 2)", "(U/C)", "(West)", "3rd", "5th", "a", "ahead", "all", "chopper", "closed", "east", "entire", "free", "frm", "gulf", "helpline", "helplines", "htt", "id", "is", "live", "me", "more", "new", "north", "old", "open", "opened", "our", "ours", "people", "planned", "plans", "plz", "restore", "rt", "service", "south", "stuff", "their", "uptodate", "us", "welcome", "west", "white", "wht", "you"]

    names_to_remove = set([x.lower() for x in names_to_remove])

    # will help in filtering out unigram location names
    gaz_stopwords = "Dictionaries/gaz_stopwords_filtered.txt"
    gaz_stopwords = set([line.strip() for line in open(gaz_stopwords, 'r')])

    # ==========================================================================
    unique_names = defaultdict(int)
    all_names = list()
    # ==========================================================================

    # step 1 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    for text in raw_names:

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

            name = name.strip()

            # skip empty names
            if name == "":
                continue

            all_names.append(name)
            unique_names[name]+=1


    # step 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    for name in all_names:

        nospaces = name.replace(" ", "")

        if len(nospaces) > 2 and not nospaces.isdigit():

            # remove all non-alphaneumeric characters
            alphanumeric_name = re.sub(r'\W+', ' ', name)
            alphanumeric_name = alphanumeric_name.strip()

            if alphanumeric_name != name and alphanumeric_name not in gaz_stopwords:
                all_names.append(alphanumeric_name)
                unique_names[alphanumeric_name] += 1

            if name not in gaz_stopwords:
                unique_names[name] += 1


    # step 3 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # create skip grams

    for name in set(unique_names):
        name_list = name.split()
        name_len = len(name_list)

        flexi_grams = list()

        if name_len > 2:
            flexi_gram = [name_list[0], name_list[name_len-1]]

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
                    base_name = map(itemgetter(0), groupby(base_name))

                    flexi_grams.append(" ".join(base_name))


        for new_name in set(flexi_grams):

            nospaces = new_name.replace(" ", "")

            if len(nospaces) > 2 and not nospaces.isdigit():

                all_names.append(new_name)
                unique_names[new_name]+=1


    return unique_names, all_names, get_extended_words3_list(unique_names)
