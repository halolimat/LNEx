import re
import os
import json
import string
import itertools
import collections
from itertools import groupby
from wordsegment import segment
from operator import itemgetter
from collections import defaultdict

printable = set(string.printable)
exclude = set(string.punctuation)

# importing local modules
import Language_Modeling
from tokenizer import Twokenize

################################################################################

# LNEx global environment
env = None

def set_global_env(g_env):
    global env
    env = g_env

################################################################################
################################################################################
################################################################################

# Stack data structure
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop(0)

    def notEmpty(self):
        return self.items != []

################################################################################

# Tree data structure. Used for building the bottom up tree of valid n-grams
class Tree:
    def __init__(
            self,
            cargo,
            left=None,
            right=None,
            level=1,
            tokensIndexes=set()):
        # the data of the node. i.e., the n-gram tokens
        self.cargo = cargo
        # left child of tree node
        self.left = left
        # right child of tree node
        self.right = right
        # unigrams are level 1 -> bigrams are level 2
        self.level = level
        # n-gram tokens indexes from the original tweet text
        self.tokensIndexes = tokensIndexes

    def __str__(self):
        return str(self.cargo)

################################################################################

def preprocess_tweet(tweet):

    # remove retweet handler
    if tweet[:2] == "rt":
        try:
            colon_idx = tweet.index(": ")
            tweet = tweet[colon_idx + 2:]
        except BaseException:
            pass

    # remove url from tweet
    tweet = re.sub(
        r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*',
        '',
        tweet)

    # remove non-ascii characters
    tweet = filter(lambda x: x in printable, tweet)

    # additional preprocessing
    tweet = tweet.replace("\n", " ").replace(" https", "").replace("http", "")

    # remove all mentions
    tweet = re.sub(r"@\w+", "", tweet)

    # extract hashtags to break them -------------------------------------------
    hashtags = re.findall(r"#\w+", tweet)

    # This will contain all hashtags mapped to their broken segments
    # e.g., #ChennaiFlood : {chennai, flood}
    replacements = defaultdict()

    for hashtag in hashtags:

        # keep the hashtag with the # symbol
        _h = hashtag[1:]

        # remove any punctuations from the hashtag and mention
        # ex: Troll_Cinema => TrollCinema
        _h = _h.translate(None, ''.join(string.punctuation))

        # breaks the hashtag
        segments = segment(_h)
        # concatenate the tokens with spaces between them
        segments = ' '.join(segments)

        replacements[hashtag] = segments

    # replacement of hashtags in tweets
    # e.g., if #la & #laflood in the same tweet >> replace the longest first
    for k in sorted(
            replacements,
            key=lambda k: len(
                replacements[k]),
            reverse=True):
        tweet = tweet.replace(k, replacements[k])

    # --------------------------------------------------------------------------

    # padding punctuations
    tweet = re.sub('([,!?():])', r' \1 ', tweet)

    tweet = tweet.replace(". ", " . ").replace("-", " ")

    # shrink blank spaces in preprocessed tweet text to only one space
    tweet = re.sub('\s{2,}', ' ', tweet)

    # remove trailing spaces
    tweet = tweet.strip()

    return tweet

################################################################################

# based on Cristian answer @ http://stackoverflow.com/questions/2158395
def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not \
           isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

################################################################################

# given the gazetteer langauge model (glm) and the tweet segment (ts), this
# function is going to build a bottom up tree of valid n-grams
def build_tree(glm, ts):

    # dictionary of valid n-grams
    valid_n_grams = defaultdict(float)

    # store tree nodes in a stack
    nodes = Stack()

    # init leaf nodes from the unigrams
    for index, token in enumerate(ts):
        nodes.push(
            Tree(
                cargo=token,
                left=None,
                right=None,
                level=1,
                tokensIndexes=set([index])))

    node1 = None
    node2 = None

    while nodes.notEmpty():

        if node1 is None:
            node1 = nodes.pop()
            node2 = nodes.pop()

        else:
            node1 = node2
            node2 = nodes.pop()

        # process nodes of similar n-gram degree/level
        if node1.level == node2.level:

            _node2 = node2

            # if there is a common child take only the right child
            if node1.right == node2.left and node1.right is not None:
                _node2 = node2.right

            tokens_list = list()

            # find valid n-grams from the cartisian product of two tree nodes
            for i in itertools.product(node1.cargo, _node2.cargo):

                # flatten the list of lists
                flattened = list(flatten(i))

                # remove consecutive duplicates
                final_list = map(itemgetter(0), groupby(flattened))

                # prune based on the probability from the language model
                p = " ".join(final_list)
                p = p.strip()

                # the probability of a phrase p calculated by the language model
                score = glm.phrase_probability(p)

                # if an n-gram is valid then add it to the dictionary
                if score > 0:

                    # e.g., ('avadi', 'rd', (4, 5))
                    valid_n_gram = tuple(final_list) + \
                                    (tuple(set(node1.tokensIndexes | \
                                    _node2.tokensIndexes)),)

                    # e.g., ('avadi', 'rd', (4, 5)) 5.67800416892e-05
                    valid_n_grams[valid_n_gram] = score

                    # the cargo of the node
                    tokens_list.append(final_list)

            # create higher level nodes and store them in the stack
            nodes.push(
                Tree(
                    tokens_list,
                    node1,
                    node2,
                    (node1.level + node2.level),
                    (node1.tokensIndexes | node2.tokensIndexes)))

    return valid_n_grams

################################################################################

# based on aquavitae answer @ http://stackoverflow.com/questions/9518806/
# tokenize the tweet and retain the offsets of each token
def using_split2(line, _len=len):
    words = Twokenize.tokenize(line)
    index = line.index
    offsets = []
    append = offsets.append
    running_offset = 0
    for word in words:
        word_offset = index(word, running_offset)
        word_len = _len(word)
        running_offset = word_offset + word_len
        append((word, word_offset, running_offset - 1))
    return offsets

################################################################################

# based on AkiRoss answer @ http://stackoverflow.com/questions/4664850
def findall(p, s):
    '''Yields all the positions of
    the pattern p in the string s.'''
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i + 1)

################################################################################

# This function will align the offsets of the preprocessed string with the
# raw string to retain original offsets when outputing spotted location names
def align_and_split(raw_string, preprocessed_string):

    tokens = list()

    last_index = 0

    for token in using_split2(preprocessed_string):

        matches = [(raw_string[i:len(token[0]) + i], i, len(token[0]) + i - 1)
                   for i in findall(token[0], raw_string)]

        for match in matches:
            if match[1] >= last_index:
                last_index = match[1]
                tokens.append(match)
                break

    return tokens

################################################################################
################################################################################

# given a tweet, this function will extract all location names from it
'''
    returns a list of the following 4 items tuple:
        tweet_mention, mention_offsets, geo_location, geo_info_id

        tweet_mention:   is the location mention in the tweet
                         (substring retrieved from the mention offsets)

        mention_offsets: a tuple of the start and end offsets of the LN

        geo_location:    the matched location name from the gazetteer.
                         e.g., new avadi rd > New Avadi Road

        geo_info_id:     contains the attached metadata of all the matched
                         location names from the gazetteer
'''
def extract(tweet):

    # check if environment was correctly initialized
    if env == None:
        print "\n##################################################"
        print "Global ERROR: LNEx environment must be initialized"
        print "##################################################\n"
        exit()

    # --------------------------------------------------------------------------

    #will contain for example: (0, 11): [(u'new avadi road', 3)]
    valid_n_grams_from_cartisian_product = defaultdict(list)

    # we will call a tweet from now onwards a query
    query = str(tweet.lower())

    preprocessed_query = preprocess_tweet(query)

    query_tokens = align_and_split(query, preprocessed_query)

    location_names_in_query = list()

    # --------------------------------------------------------------------------
    # prune the tree of locations based on the exisitence of stop words
    # by splitting the query into multiple queries
    query_splits = Twokenize.tokenize(query)
    stop_in_query = env.stopwords_notin_gazetteer & set(query_splits)

    # if tweet contains the following then remove them from the tweet and
    # split based on their presence:
    stop_in_query = stop_in_query | set(
        ["[", "]", ".", ",", "(", ")", "!", "?", ":", "<", ">", "newline"])

    # remove stops from query
    for index, token in enumerate(query_tokens):
        if token[0] in stop_in_query:
            query_tokens[index] = ()

    # combine consecutive tokens in a query as possible location names
    query_filtered = list()
    candidate_location = {"tokens": list(), "offsets": list()}

    for index, token in enumerate(query_tokens):

        if len(token) > 0:
            candidate_location["tokens"].append(token[0].strip())
            candidate_location["offsets"].append((token[1], token[2]))

        elif candidate_location != "":
            query_filtered.append(candidate_location)
            candidate_location = {"tokens": list(), "offsets": list()}

        # if I am at the last token in the list
        # ex: "new avadi road" then it wont be added unless I know that this is
        #        the last token then append whatever you have
        if index == len(query_tokens) - 1:
            query_filtered.append(candidate_location)

    ##########################################################################

    # start the core extraction procedure using the bottom up trees
    for sub_query in query_filtered: # ----------------------------------- for I

        sub_query_tokens = sub_query["tokens"]
        sub_query_offsets = sub_query["offsets"]

        # expand tokens in sub_query_tokens to vectors
        for idx, token in enumerate(sub_query_tokens): # ---------------- for II

            token_edited = ''.join(ch for ch in token if ch not in exclude)

            # if the token is for sure misspilled
            if  token not in env.extended_words3 and \
                token_edited not in env.extended_words3:

                sub_query_tokens[idx] = [token]

                # expand the token into the full name without abbreviations.
                # Ex=> rd to road
                token_exp = env.streets_suffixes_dict.get(token)
                if token_exp and token_exp not in sub_query_tokens[idx]:
                    sub_query_tokens[idx].append(token_exp)

            # do not expand the word if it is not misspilled
            else:

                loc_name = sub_query_tokens[idx]

                sub_query_tokens[idx] = [sub_query_tokens[idx]]

                # expand the token into the full name without abbreviations.
                # Ex=> rd to road
                token_exp = env.streets_suffixes_dict.get(loc_name)
                if token_exp and token_exp not in sub_query_tokens[idx]:
                    sub_query_tokens[idx].append(token_exp)

                sub_query_tokens[idx] = list(set(sub_query_tokens[idx]))


            # ------------------------------------------------------------------

            # Expand a token to its abbreviation and visa versa
            exp_words = list()
            for x in sub_query_tokens[idx]:
                if x in set(env.osm_abbreviations):
                    exp_words += env.osm_abbreviations[x]

            sub_query_tokens[idx] += exp_words

        # ----------------------------------------------------------- End for II

        valid_n_grams = defaultdict(float)

        # this would build the bottom up tree of valid n-grams
        # if the query contains more than one vector then build the tree
        if len(sub_query_tokens) > 1:

            valid_n_grams = build_tree(env.glm, sub_query_tokens)

            # imporoving recall by adding unigram location names ++++++++++++++

            already_assigned_locations_tokens = list()

            for valid_n_gram in valid_n_grams:
                for token_index in valid_n_gram[-1]:
                    already_assigned_locations_tokens.append(token_index)

            for x in range(len(sub_query_tokens)):
                if x not in already_assigned_locations_tokens:

                    for token_match in sub_query_tokens[x]:

                        if token_match in env.gazetteer_unique_names_set:
                            valid_n_grams[(token_match, (x,))] = 1

        # when the size of the subquery is only one token
        elif len(sub_query_tokens) == 1:

            for token in sub_query_tokens[0]:
                valid_n_grams[(token, (0,))] = env.glm.phrase_probability(token)

        # ----------------------------------------------------------------------

        for valid_n_gram in valid_n_grams:

            # sort the offsets
            # e.g., valid_n_gram = ("token", "token", (index-1, index-2))
            offsets = sorted([sub_query_offsets[token_idx]
                              for token_idx in valid_n_gram[-1]])

            # the start index of the first token
            start_idx = offsets[0][0]
            # the end index of the last token
            end_idx = offsets[-1][1]

            # contains the matched location name from cartisian product
            mached_ln = " ".join(valid_n_gram[:-1])

            index_tub = (start_idx, end_idx + 1)

            number_of_tokens = len(valid_n_gram[:-1])

            valid_n_grams_from_cartisian_product[index_tub].append(
                (mached_ln, number_of_tokens))

            #tub = ((start_idx, end_idx + 1),
            #       valid_n_grams[valid_n_gram])

            tub = ((start_idx, end_idx + 1),
                   ">>>")

            location_names_in_query.append(tub)

        # ----------------------------------------------------------------------

        # if length is zero means no more than unigrams were found in the query
        if len(valid_n_grams) == 0:

            for index, value in enumerate(sub_query_tokens):

                max_prob_reco = ("", 0)

                for y in value: # ----------------------------------------------

                    # if the unigram is an actual full location name
                    if y in env.gazetteer_unique_names_set:
                        if max_prob_reco[1] < len(
                                env.gazetteer_unique_names[y]):
                            max_prob_reco = (
                                y, len(env.gazetteer_unique_names[y]))

                # --------------------------------------------------------------

                # this is the solution for only one grams found in the sentence
                if max_prob_reco[1] > 0:

                    # here we add the unigram toponyms found in query

                    tub_1 = sub_query_offsets[index][0]
                    tub_2 = sub_query_offsets[index][1] + 1

                    # tuble would have: ((start_idx,end_idx),prob)
                    tub = ((tub_1, tub_2), ">>>>")

                    location_names_in_query.append(tub)

                    tub = (tub_1, tub_2)

                    mached_ln = max_prob_reco[0]

                    number_of_tokens = mached_ln.count(" ") + 1

                    valid_n_grams_from_cartisian_product[tub].append(
                        (mached_ln, number_of_tokens))

    # ---------------------------------------------------------------- end for I

    location_names_in_query = list(set(location_names_in_query))

    location_names_in_query = filterout_overlaps(
        location_names_in_query,
        env.gazetteer_unique_names_set,
        valid_n_grams_from_cartisian_product)

    # set of: ((offsets), probability), full_mention)
    location_names_in_query = remove_non_full_mentions(
        location_names_in_query,
        env.gazetteer_unique_names_set,
        valid_n_grams_from_cartisian_product,
        query_tokens)

    # --------------------------------------------------------------------------

    # list of > (tweet_mention, offsets, geo_location, geo_info)
    final_lns = list()

    for ln in location_names_in_query:

        tweet_mention = tweet[ln[0][0][0]:ln[0][0][1]]
        mention_offsets = (ln[0][0][0], ln[0][0][1])
        geo_location = ln[1]
        geo_info_ids = env.gazetteer_unique_names[ln[1]]

        final_lns.append((  tweet_mention,
                            mention_offsets,
                            geo_location,
                            geo_info_ids))

    return final_lns

################################################################################

def do_they_overlay(tub1, tub2):

    if tub2[1] >= tub1[0] and tub1[1] >= tub2[0]:
        return True

################################################################################

def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

################################################################################

def remove_non_full_mentions(
        tops,
        gazetteer_unique_names_set,
        valid_n_grams_from_cartisian_product,
        query_tokens):

    original_set = set(tops)

    # would contain the following:
    # ((offsets), probability), full_mention)
    final_set = set()

    for x in original_set:
        tops_name = valid_n_grams_from_cartisian_product[x[0]]

        found = False

        for top_name in tops_name:
            if top_name[0] in gazetteer_unique_names_set:

                final_set.add((x, top_name[0]))
                found = True
                break

        # if not found then try to find a full name inside the non full name
        # search for full mentions inside those non full mentions. Ex. The
        # Louisiana > Louisiana | Louisiana and > Louisiana
        if not found:
            # ex: the louisiana => (49, 62)
            for top in tops_name:

                top_tokens = top[0].split()

                for gram_len in range(len(top_tokens) - 1, -1, -1):
                    for gram in find_ngrams(top_tokens, gram_len + 1):
                        candidate_top = " ".join(gram)

                        # if it is a full mention then get the offsets from the
                        # query_tokens list
                        if candidate_top in gazetteer_unique_names_set:
                            # print "candidate_top", candidate_top

                            # get the indecies from the original query tokens
                            for query_token in query_tokens:
                                if query_token:
                                    token_min_range = x[0][0]
                                    token_max_range = (x[0][1]) - 1

                                    if token_min_range <= query_token[1] and \
                                            token_max_range >= query_token[2] and \
                                            candidate_top == query_token[0]:
                                        # print "GOT IT", query_token,
                                        # candidate_top

                                        t = (
                                            (query_token[1], query_token[2] + 1), 1)

                                        t = (t, candidate_top)

                                        final_set.add(t)

    return final_set

################################################################################

def filterout_overlaps(tops, gazetteer_unique_names_set,
                       valid_n_grams_from_cartisian_product):
    '''
    Evangeline Parish Sheriff

    Evangeline Parish is being chosen eventhough the full should be taken

    '''

    original_set = set(tops)

    full_location_names = list()
    lengths = list()

    for x in original_set:
        tops_name = valid_n_grams_from_cartisian_product[x[0]]

        for top_name in tops_name:
            if top_name[0] in gazetteer_unique_names_set:
                full_location_names.append(x)
                lengths.append(top_name[1])
                break

    # remove the overlap between full location mentions:
    # >> preferring the longest
    # NOTE: for now will try to keep both if they have same length
    for x in range(len(full_location_names)):
        for y in range(x + 1, len(full_location_names)):

            ranges_1 = full_location_names[x][0]
            ranges_2 = full_location_names[y][0]

            try:

                if do_they_overlay(ranges_1, ranges_2):
                    if lengths[x] > lengths[y]:
                        original_set.remove(full_location_names[y])
                    else:
                        original_set.remove(full_location_names[x])

            except BaseException:
                pass

    # remove all that overlap with this mention and leave the rest

    longest_full_location_names = original_set & set(full_location_names)
    # print "intersection: > ", longest_full_location_names

    final_set = set(original_set)

    for lon_top in longest_full_location_names:
        for top in original_set:

            if lon_top != top:

                if do_they_overlay(lon_top[0], top[0]):

                    try:
                        final_set.remove(top)
                    except BaseException:
                        pass

    return final_set

##########################################################################
##########################################################################

class init_env:

    def __init__(self, geo_locations, extended_words3):

        ###################################################
        # OSM abbr dictionary
        ###################################################

        dicts_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "_Dictionaries/")

        fname = dicts_dir + "osm_abbreviations.csv"

        # read lines to list
        with open(fname) as f:
            lines = f.read().splitlines()

        self.osm_abbreviations = defaultdict(list)

        for x in lines:
            line = x.split(",")

            # apartments > apts
            self.osm_abbreviations[line[0]].append(line[1])
            # apartments > apts.
            self.osm_abbreviations[line[0]].append(line[1] + ".")

            # apts > apartments
            self.osm_abbreviations[line[1]].append(line[0])
            # apts. > apartments
            self.osm_abbreviations[line[1] + "."].append(line[0])

        #######################################################################

        self.gazetteer_unique_names = geo_locations

        self.gazetteer_unique_names_set = set(
            self.gazetteer_unique_names.keys())

        # NOTE BLACKLIST CODE GOES HERE

        # this list has all the english words in addition to the names
        # from the combined gazetteer, any word not in the list is
        # considered misspilled.

        self.extended_words3 = extended_words3
        self.extended_words3 = set(self.extended_words3)

        #######################################################################

        streets_suffixes_dict_file = dicts_dir + "streets_suffixes_dict.json"

        with open(streets_suffixes_dict_file) as f:

            self.streets_suffixes_dict = json.load(f)

        #######################################################################

        # gazetteer-based language model
        self.glm = Language_Modeling.GazBasedModel(geo_locations)

        #######################################################################

        # list of unigrams
        unigrams = self.glm.unigrams["words"].keys()

        self.stopwords_notin_gazetteer = set(
            self.extended_words3) - set(unigrams)


def initialize(geo_locations, extended_words3):

    print "Initializing LNEx ..."
    g_env = init_env(geo_locations, extended_words3)
    set_global_env(g_env)
    print "Done Initialization ..."
