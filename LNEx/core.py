import numpy
import itertools
import collections

import re, string, json
from itertools import groupby
from operator import itemgetter
import csv, sys, os, datetime, time
from collections import defaultdict

printable = set(string.printable)
exclude = set(string.punctuation)

# importing local modules

from wordsegment import segment
import Language_Modeling
from tokenizer import Twokenize

from tabulate import tabulate

import osm_gazetteer

################################################################################
################################################################################
################################################################################

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop(0)

    def notEmpty(self):
        return self.items != []

class Tree:
    def __init__(self, cargo, left=None, right=None, isCoupled=False, level=1, tokensIndexes=set()):
        self.cargo = cargo
        self.left  = left
        self.right = right
        self.isCoupled = isCoupled
        self.level = level
        self.tokensIndexes = tokensIndexes

    def __str__(self):
        return str(self.cargo)


################################################################################
################################################################################

def preprocess_tweet(tweet):

    # remove retweet handler
    if tweet[:2] == "rt":
        try:
            colon_idx = tweet.index(": ")
            tweet = tweet[colon_idx+2:]
        except:
            pass

    # remove url from tweet
    tweet = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', tweet)

    # remove non-ascii characters
    tweet = filter(lambda x: x in printable, tweet)
    #tweet = tweet.encode('ascii',errors='ignore')

    # additional preprocessing
    tweet = tweet.replace("\n", " ").replace(" https","").replace("http","")

    # remove all mentions
    tweet = re.sub(r"@\w+", "", tweet)

    # break hashtags +++++++++++++
    hashtags = re.findall(r"#\w+", tweet)

    replacements = defaultdict()

    #NOTE: #Ramapuram is being broken, we should check in the unigrams before breaking it
    for term in hashtags:

        token = term[1:]

        # remove any punctuations from the hashtag and mention
        # ex: Troll_Cinema => TrollCinema
        token = token.translate(None, ''.join(string.punctuation))

        segments = segment(token)
        segments = ' '.join(segments)

        replacements[term] = segments

        #tweet = tweet.replace(term, segments)

    # fix replacement of hashtags
    # #la #laflood >> replace the longest first
    for k in sorted(replacements, key=lambda k: len(replacements[k]), reverse=True):
        tweet = tweet.replace(k, replacements[k])

    #+++++++++++++++++++++++++++++++++++++++++++
    # padding punctuation
    #tweet = re.sub('([.,!?()-])', r' \1 ', tweet)
    tweet = re.sub('([,!?():])', r' \1 ', tweet)

    tweet = tweet.replace(". ", " . ")
    tweet = tweet.replace("-", " ")

    tweet = re.sub('\s{2,}', ' ', tweet)

    # remove trailing spaces
    tweet = tweet.strip()

    return tweet


# based on: http://stackoverflow.com/questions/2158395
def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def build_tree(glm, q):

    possible_locations = defaultdict(float)

    nodes = Stack()

    # init leaf nodes
    for index, token in enumerate(q):
        nodes.push(Tree(cargo=token, left=None, right=None, isCoupled=False, level=1, tokensIndexes=set([index])))

    node1 = None
    node2 = None

    while nodes.notEmpty():

        if node1 is None:
            node1 = nodes.pop()
            node2 = nodes.pop()

        else:
            node1 = node2
            node2 = nodes.pop()

        if node1.level == node2.level:

            grams_list = list()

            secondNode = node2

            # if there is a common child take only the right child
            if node1.right == node2.left and node1.right is not None:
                secondNode = node2.right

            for i in itertools.product(node1.cargo, secondNode.cargo):

                # flatten the list
                flattened = list(flatten(i))

                # remove consecutive duplicates
                final_list = map(itemgetter(0), groupby(flattened))

                # prune based on the probability from the language model
                np = " ".join(final_list)
                np = np.strip()

                score = glm.phrase_probability(np)

                if score > 0:
                    grams_list_key = tuple(final_list) + (tuple(set(node1.tokensIndexes|secondNode.tokensIndexes)),)

                    #print grams_list_key

                    possible_locations[grams_list_key] = score

                    grams_list.append(final_list)


            nodes.push(Tree(grams_list, node1, node2, False, (node1.level+node2.level), (node1.tokensIndexes | node2.tokensIndexes )))

    return possible_locations

################################################################################
################################################################################
################################################################################

#source: http://stackoverflow.com/questions/9518806/
def using_split2(line, _len=len):
    #words = line.split()
    #words = tknzr.tokenize(line)
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

def findall(p, s):
    '''Yields all the positions of
    the pattern p in the string s.'''
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)

# a is the raw string
# b is the preprocessed string
def align_and_split(a, b):

    tokens = list()

    last_index = 0

    for token in using_split2(b):

        matches = [(a[i:len(token[0])+i], i, len(token[0])+i-1) for i in findall(token[0], a)]

        for match in matches:
            if match[1] >= last_index:
                last_index = match[1]
                tokens.append(match)
                break

    return tokens

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

def extract(env, tweet):

    '''
    will contain for example:

    defaultdict(<type 'list'>, {(0, 11): [(u'new avadi road', 3)], (0, 8): [(u'new avadi', 2)], (4, 11): [(u'avadi rd', 2), (u'avvai road', 2), (u'avadi road', 2)]})

    '''
    location_names_from_cartisian_product = defaultdict(list)

    query = tweet

    original_query = str(query)

    #print "original_query =>>> ", original_query
    #print

    query = str(query.lower())

    # remove the keywords used to crawl from tweet text
    #query = query.translate(None, ''.join(kw))

    preprocessed_query = preprocess_tweet(query)
    # volunteer/offer > volunteer offer
    #preprocessed_query = preprocessed_query.replace("/", "")

    query_tokens = align_and_split(query, preprocessed_query)

    # @dev
    #print "QQQQ> query_tokens >>> ", query_tokens

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    toponyms_in_query = list()

    ############################################################################
    # prune the tree of locations based on the exisitence of stop words
    # by splitting the query into multiple queries
    #query_splits = tknzr.tokenize(query)
    query_splits = Twokenize.tokenize(query)
    stop_in_query = env.stopwords_notin_gazetteer & set(query_splits)
    #stop_in_query = stopwords_notin_gazetteer & set(query.split())

    # if tweet contains the following then remove them from the tweet and
    # split based on their presence: ["[", "]",".", ",", "(", ")", "!", "?"]
    stop_in_query = stop_in_query | set(["[", "]",".", ",", "(", ")", "!", "?", ":", "<", ">", "newline"])

    # remove stops from query
    for index, token in enumerate(query_tokens):
        if token[0] in stop_in_query:
            query_tokens[index] = ()

    # combine consecutive tokens in query as possible toponym name
    query_filtered = list()
    candidate_location = {"tokens": list(), "offsets": list()}

    for index, token in enumerate(query_tokens):
        #print token
        if len(token) > 0:
            candidate_location["tokens"].append(token[0].strip())
            candidate_location["offsets"].append((token[1],token[2]))

        elif candidate_location != "":
            query_filtered.append(candidate_location)
            candidate_location = {"tokens": list(), "offsets": list()}

        # if I am at the last token in the list
        # ex: "new avadi road" then it wont be added unless I know that this is
        #        the last token then append whatever you have
        if index == len(query_tokens)-1:
            query_filtered.append(candidate_location)

    #print query_filtered

    #sys.exit()

    ############################################################################
    # contains the token in query to the correct toponym
    # ex > new avad rd > new avadi road
    #query_toponyms = defaultdict()

    # build vectors for each token in each subquery
    for sub_query in query_filtered:

        sub_query_tokens = sub_query["tokens"]
        sub_query_offsets = sub_query["offsets"]

        #print "sub_query_tokens >>> ", sub_query_tokens

        original_subquery = " ".join(sub_query_tokens)

        '''
        # generate all-grams of q
        all_grams = list()
        for i in reversed(range(len(q))):
            i_grams = ngrams(q, i+1)
            for grams in i_grams:
                all_grams.append(grams)


        # check scores of all grams
        for gram in all_grams:

            gram_txt = " ".join(gram)
            print len(gram), gram, lm.phrase_probability(gram_txt)

        continue
        '''

        # expand tokens in sub_query_tokens to vectors
        for idx, token in enumerate(sub_query_tokens):

            # @dev
            #print "````````) ", token

            token_edited = ''.join(ch for ch in token if ch not in exclude)

            # is the token is for sure misspilled
            if token not in env.extended_longlist_stopwords and token_edited not in env.extended_longlist_stopwords:

                #print "token ???? ", token

                # TODO: unigrams_set make it indexed on the first letter instead of searching all unigrams,, them search only unigrams with same first letter.
                #matches = [(x, difflib.SequenceMatcher(None, x, token).ratio()) for x in unigrams]

                #matches = [(x, difflib.SequenceMatcher(None, x, token).ratio()) for x in unigrams_set_indexed_first_letter[token[0]]]
                #matches = filter(lambda x: x[1]>0.65, matches)
                #NOTE: the vector of matched locations should be sorted with descending order of similarity. This will be helpful when matching unigrams and break whenever we have a full name match instead of looping all list
                #matches = sorted(matches, key=lambda x: x[1], reverse=True)

                # only return the terms without scores
                #sub_query_tokens[idx] = [x[0] for x in matches]

                sub_query_tokens[idx] = [token]

                # expand the token into the full name without abbreviations. Ex=> rd to road
                token_exp = env.streets_suffixes_dict.get(token)
                if token_exp and token_exp not in sub_query_tokens[idx]:
                    sub_query_tokens[idx].append(token_exp)


                '''# expand list of alternatvies in the wordvec with the geo abbreviation

                addition = list()

                for word in sub_query_tokens[idx]:
                    word = pattern.sub('', word)

                    geo_abbrevs = geo_abbreviations_fixed.get(word)

                    if geo_abbrevs:
                        #print "geo_abbrevs",geo_abbrevs

                        for ab in geo_abbrevs:
                            if not ab == "":
                                addition.append(ab)

                if len(addition) > 0:
                    sub_query_tokens[idx] = sub_query_tokens[idx] + addition'''

            # do not expand the word if it is inside the extended version of words3
            else:

                #print "ELSE"

                loc_name = sub_query_tokens[idx]

                #print q[idx], "\t", "%.20f" % lm.phrase_probability(q[idx])

                sub_query_tokens[idx] = [sub_query_tokens[idx]]

                # expand the token into the full name without abbreviations. Ex=> rd to road
                token_exp = env.streets_suffixes_dict.get(loc_name)
                if token_exp and token_exp not in sub_query_tokens[idx]:
                    sub_query_tokens[idx].append(token_exp)

                # get matches from the unigrams to be able to get
                # records like > Tamilnadu
                #matches = [(x, difflib.SequenceMatcher(None, x, loc_name).ratio()) for x in inverted_index_unigrams_to_unique_names]
                #matches = filter(lambda x: x[1]>0.9, matches)
                #sub_query_tokens[idx] = sub_query_tokens[idx] + [x[0] for x in matches]

                sub_query_tokens[idx] = list(set(sub_query_tokens[idx]))

                ##############>>>

                #list_full_names = list()
                #for x in sub_query_tokens[idx]:
                #    list_full_names = list_full_names + inverted_index_unigrams_to_unique_names[x]

                ## TODO: fix bottleneck here
                '''
                ################################################################
                # if exisits in the gazetteer but also there is
                # another record in the gazetteer with high score
                # add it also as a candidate. Ex-> Tamilnadu & Tamil Nadu
                #>>>> solved using gazetteer_unique_names_set , but slow

                # get matches from the unique names> to be able to get more than unigrams. Ex: Tamil Nadu
                matches = [(x, difflib.SequenceMatcher(None, x, loc_name).ratio()) for x in unique_names_by_first_letter[loc_name[0]]]
                matches = filter(lambda x: x[1]>0.9, matches)

                # this make sure that the first letter of the
                # name is the same as the first letter in the
                # matched name
                matches = filter(lambda x: x[0][0] == loc_name[0], matches)

                sub_query_tokens[idx] = sub_query_tokens[idx] + [x[0] for x in matches]
                sub_query_tokens[idx] = list(set(sub_query_tokens[idx]))
                ################################################################
                '''

                '''# expand list of alternatvies in the wordvec with the geo abbreviation

                addition = list()

                for word in sub_query_tokens[idx]:
                    word = pattern.sub('', word)

                    geo_abbrevs = geo_abbreviations_fixed.get(word)

                    if geo_abbrevs:
                        #print "geo_abbrevs",geo_abbrevs

                        for ab in geo_abbrevs:
                            if not ab == "":
                                addition.append(ab)

                if len(addition) > 0:
                    sub_query_tokens[idx] = sub_query_tokens[idx] + addition'''

            #NOTE: does it make sense if we remove all matches which does not
            #       have the first charcter in common with the original token

            # 00000000000000000000000000000000000000000000000000000000000000
            # 00000000000000000000000000000000000000000000000000000000000000
            # Expand a token to its abbreviation and visa versa
            exp_words = list()
            for x in sub_query_tokens[idx]:
                if x in set(env.osm_abbreviations):
                    exp_words += env.osm_abbreviations[x]
                    #print "env.osm_abbreviations>>>", x

            sub_query_tokens[idx] += exp_words

            #print "###############", sub_query_tokens[idx]

        # @dev
        #print sub_query_tokens
        #print "sub_query_tokens>>>", "*"*100

        #print "===================>", q
        #print lm.phrase_probability("saidapet flyover")
        #sys.exit()

        # remove empty vectors in list
        #NOTE: if we want to do that we should retain the original index
        #       of each token to later be correctly mapped to the original token
        #       ex:> ""0, "xxx"1, "yyy"2 > "xxx"1, "yyy"2
        #sub_query_tokens = [v for v in sub_query_tokens if len(v)>0]

        #NOTE: eb offices > in gazetteer > eb office > multiple records
        # in the next step offices would mean all the records of eb office
        # also: xxx mosque | yyy mosque > "all mosques" should be reduced to all xxx and yyy
        #print sub_query_tokens

        possible_locations = defaultdict(float)

        # this would build a tree of candidate location names from
        # bottom up as in the build_tree_example function
        # if the query contains more than one vector then build the tree
        if len(sub_query_tokens) > 1:

            possible_locations = build_tree(env.glm, sub_query_tokens)

            # @dev
            #print "LEN > 1"
            #print
            #print "#######>", possible_locations
            #print

            # imporoving recall by adding unigram location names +++++++++++++++

            already_assigned_locations_tokens = list()

            for x in possible_locations:
                for token_index in x[-1]:
                    already_assigned_locations_tokens.append(token_index)

            for x in range(len(sub_query_tokens)):
                if x not in already_assigned_locations_tokens:

                    for token_match in sub_query_tokens[x]:

                        if token_match in env.gazetteer_unique_names_set:
                            possible_locations[(token_match, (x,))] = 1

            # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        elif len(sub_query_tokens) == 1:

            # @dev
            #print "LEN = 1"

            for token in sub_query_tokens[0]:
                possible_locations[(token, (0,))] = env.glm.phrase_probability(token)
        else:

            # @dev
            #print "<no match with any unigram from the gazetteer>"

            pass


        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

        for possible_location in possible_locations:

            #possible_location = ("token", "token", (index-1, index-2))
            offsets = [sub_query_offsets[token_idx]
                            for token_idx in possible_location[-1]]

            # TODO: fix the sortings in previous code
            # sort the offsets
            offsets.sort()

            # the start index of the first token
            start_idx = offsets[0][0]
            # the end index of the last token
            end_idx = offsets[-1][1]

            #NOTE: this will contain the matched/corrected name
            #           needed for the disambiguation part

            # contains the fuzzy matched location name fro cartisian product
            fuzzy_mached_top = " ".join(possible_location[:-1])

            index_tub = (start_idx, end_idx+1)

            number_of_tokens = len(possible_location[:-1])

            location_names_from_cartisian_product[index_tub].append((fuzzy_mached_top, number_of_tokens))

            tub = ((start_idx, end_idx+1), possible_locations[possible_location])

            # @dev
            #print "tub >>>>>>>", fuzzy_mached_top

            #TODO: here we can check if the fuzzy matched is a full mention
            # or partial mention and if not full to check if its sub parts
            # are full mentions> example: adyar chennai

            toponyms_in_query.append(tub)

        '''#TODO: figure out a way to map sub-query tokens to original tokens
        # down should be fixed too
        query_token = original_subquery.split()[index]
        extracted_top = max_prob_reco[0]
        query_toponyms[query_token] = extracted_top'''

        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

        # if length is zero means no more than unigrams were found in the query
        #TODO: should also loop through the list to get the unigrams that are not part of any n-gram matches. >> this should be implemented inside building the tree removing the unigram that is part of a longer gram and keep the unigrams that are not part of anything.
        if len(possible_locations) == 0:

            # @dev
            #print "+"*50, "No Results"

            # if only unigrams were found then get the best ones among them based:
            # 1- if the unigram is an actual full location name
            # 2- if the unigram is part of a location name of less than length of threshold-grams

            # since flexi_grams are used now, we should not use more than 2
            threshold = 2

            for index, value in enumerate(sub_query_tokens):

                max_prob_reco = ("",0)

                for y in value:

                    # 1
                    if y in env.gazetteer_unique_names_set:
                        if max_prob_reco[1] < len(env.gazetteer_unique_names[y]):
                            max_prob_reco = (y, len(env.gazetteer_unique_names[y]))


                    #print y,  "\t%.20f" % lm.phrase_probability(y)


                    # 2
                    # this should be used to expand implicit ones
                    # ex. airport > chennai airport
                    '''if y in inverted_index_unigrams_to_unique_names:
                        print "----------", y

                        for xxx in inverted_index_unigrams_to_unique_names[y]:
                            if len(xxx.split()) < threshold and y != "road":
                                print xxx'''


                # this is the solution for only one grams found in the sentence
                if max_prob_reco[1] > 0:

                    # here we add the unigram toponyms found in query

                    tub_1 = sub_query_offsets[index][0]
                    tub_2 = sub_query_offsets[index][1]+1

                    # tuble would have: ((start_idx,end_idx),prob)
                    tub = ((tub_1, tub_2), max_prob_reco[1])

                    toponyms_in_query.append(tub)

                    ####################
                    ###########NOTE: here add fuzzy matched name

                    #NOTE: this will contain the matched/corrected name
                    #needed for the disambiguation part

                    # contains the fuzzy matched location name fro cartisian product

                    tub = (tub_1, tub_2)

                    fuzzy_mached_top = max_prob_reco[0]

                    number_of_tokens = fuzzy_mached_top.count(" ") + 1

                    location_names_from_cartisian_product[tub].append((fuzzy_mached_top, number_of_tokens))


    toponyms_in_query = list(set(toponyms_in_query))

    toponyms_in_query = filterout_overlaps(toponyms_in_query, env.gazetteer_unique_names_set, location_names_from_cartisian_product)

    # set of > ((offsets), probability), full_mention)
    toponyms_in_query = remove_non_full_mentions(toponyms_in_query, env.gazetteer_unique_names_set, location_names_from_cartisian_product, query_tokens)

    # set of > (tweet_mention, offsets, geo_location)
    toponyms_in_query = [(tweet[x[0][0][0]:x[0][0][1]], (x[0][0][0], x[0][0][1]), x[1]) for x in toponyms_in_query]

    return toponyms_in_query


def do_they_overlay(tub1, tub2):

    if tub2[1] >= tub1[0] and tub1[1] >= tub2[0]:
        return True

# as in http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
def find_ngrams(input_list, n):
  return zip(*[input_list[i:] for i in range(n)])


def remove_non_full_mentions(tops, gazetteer_unique_names_set, location_names_from_cartisian_product, query_tokens):

    original_set = set(tops)

    # would contain the following:
    # ((offsets), probability), full_mention)
    final_set = set()

    for x in original_set:
        tops_name = location_names_from_cartisian_product[x[0]]

        found = False

        for top_name in tops_name:
            if top_name[0] in gazetteer_unique_names_set:

                final_set.add((x, top_name[0]))
                found = True
                break

        # if not found then try to find a full name inside the non full name
        # search for full mentions inside those non full mentions. Ex. The Louisiana > Louisiana | Louisiana and > Louisiana
        if not found:
            # ex: the louisiana => (49, 62)
            for top in tops_name:

                top_tokens = top[0].split()

                for gram_len in range(len(top_tokens)-1,-1,-1):
                    for gram in find_ngrams(top_tokens, gram_len+1):
                        candidate_top = " ".join(gram)

                        # if it is a full mention then get the offsets from the
                        # query_tokens list
                        if candidate_top in gazetteer_unique_names_set:
                            #print "candidate_top", candidate_top

                            # get the indecies from the original query tokens
                            for query_token in query_tokens:
                                if query_token:
                                    token_min_range = x[0][0]
                                    token_max_range = (x[0][1])-1

                                    if token_min_range <= query_token[1] and \
                                        token_max_range >= query_token[2] and \
                                        candidate_top == query_token[0]:
                                        #print "GOT IT", query_token, candidate_top

                                        t = ((query_token[1], query_token[2]+1), 1)

                                        t = (t, candidate_top)

                                        final_set.add(t)

    return final_set


def filterout_overlaps(tops, gazetteer_unique_names_set, location_names_from_cartisian_product):

    '''
    Evangeline Parish Sheriff

    Evangeline Parish is being chosen eventhough the full should be taken

    '''

    original_set = set(tops)

    full_location_names = list()
    lengths = list()

    for x in original_set:
        tops_name = location_names_from_cartisian_product[x[0]]

        for top_name in tops_name:
            if top_name[0] in gazetteer_unique_names_set:
                full_location_names.append(x)
                lengths.append(top_name[1])
                break

    # remove the overlap between full location mentions:
    # >> preferring the longest
    # NOTE: for now will try to keep both if they have same length
    for x in range(len(full_location_names)):
        for y in range(x+1, len(full_location_names)):

            ranges_1 = full_location_names[x][0]
            ranges_2 = full_location_names[y][0]

            try:

                if do_they_overlay(ranges_1, ranges_2):
                    if lengths[x] > lengths[y]:
                        original_set.remove(full_location_names[y])
                    else:
                        original_set.remove(full_location_names[x])

            except:
                pass

    # remove all that overlap with this mention and leave the rest

    longest_full_location_names = original_set & set(full_location_names)
    #print "intersection: > ", longest_full_location_names

    final_set = set(original_set)

    for lon_top in longest_full_location_names:
        for top in original_set:

            if lon_top != top:

                if do_they_overlay(lon_top[0], top[0]):

                    try:
                        final_set.remove(top)
                    except:
                        pass

    return final_set

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
################################################################################
################################################################################

class init_env:

    def __init__(self, geo_locations, extended_longlist_stopwords):

        ###################################################
        # OSM abbr dictionary
        ###################################################

        fname = "_Dictionaries/osm_abbreviations_filtered_lowercase.csv"

        # read lines to list
        with open(fname) as f:
            lines = f.read().splitlines()

        self.osm_abbreviations = defaultdict(list)

        for x in lines:
            line = x.split(",")

            # apartments > apts
            self.osm_abbreviations[line[0]].append(line[1])
            # apartments > apts.
            self.osm_abbreviations[line[0]].append(line[1]+".")

            # apts > apartments
            self.osm_abbreviations[line[1]].append(line[0])
            # apts. > apartments
            self.osm_abbreviations[line[1]+"."].append(line[0])

        ########################################################################

        self.gazetteer_unique_names = geo_locations

        self.gazetteer_unique_names_set = set(self.gazetteer_unique_names.keys())


        #NOTE BLACKLIST CODE GOES HERE

        # this list has all the english words in addition to the names
        # from the combined gazetteer, any word not in the list is
        # considered misspilled.

        self.extended_longlist_stopwords = extended_longlist_stopwords
        self.extended_longlist_stopwords = set(self.extended_longlist_stopwords)

        ########################################################################

        streets_suffixes_dict_file = "_Dictionaries/streets_suffixes_dict.json"

        with open(streets_suffixes_dict_file) as f:

            self.streets_suffixes_dict = json.load(f)

        ############################################################################

        # gazetteer-based language model
        self.glm = Language_Modeling.GazBasedModel(geo_locations)

        ############################################################################

        #list of unigrams
        unigrams = self.glm.unigrams["words"].keys()

        self.stopwords_notin_gazetteer = set(self.extended_longlist_stopwords) - set(unigrams)
