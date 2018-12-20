"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

import os
import json
import unicodedata
from tabulate import tabulate
from collections import defaultdict, OrderedDict

import sys
sys.path.append('..')
import LNEx as lnex

import operator

################################################################################
################################################################################

def do_they_overlap(tub1, tub2):
    '''Checks whether two substrings of the tweet overlaps based on their start
    and end offsets.'''

    if tub2[1] >= tub1[0] and tub1[1] >= tub2[0]:
        return True

def read_annotations(filename):

    filename = os.path.join("..", "_Data/Brat_Annotations", filename)

    # read tweets from file to list
    with open(filename) as f:
        data = json.load(f)

    return data

def write_to_file(filename, data):

    filename = os.path.join("..", "_Data/Brat_Annotations", filename)

    with open(filename, "w") as f:
        json.dump(data, f)

def fix_ann_names(filename):

    anns = read_annotations(filename)

    counter = 0

    for key in anns:
        for ann in anns[key]:
            if ann != "text":

                if anns[key][ann]['type'] == 'Toponym':
                    anns[key][ann]['type'] = 'inLoc'
                elif anns[key][ann]['type'] == 'Imp-Top':
                    anns[key][ann]['type'] = 'ambLoc'
                elif anns[key][ann]['type'] == 'Out-Top':
                    anns[key][ann]['type'] = 'outLoc'
                else:
                    if anns[key][ann]['type'] not in ['inLoc', 'outLoc', 'ambLoc']:
                        print anns[key][ann]['type']
        #counter += 1
        #print counter

    write_to_file(filename, anns)

################################################################################

def init_using_files():

    data_folder = os.path.join("..", "_Data")

    with open(data_folder+"/chennai_geo_locations.json") as f:
        geo_locations = json.load(f)

    with open(data_folder+"/chennai_geo_info.json") as f:
        geo_info = json.load(f)

    with open(data_folder+"/chennai_extended_words3.json") as f:
        extended_words3 = json.load(f)

    lnex.initialize_using_files(geo_locations, extended_words3)

    return geo_info

def init_using_elasticindex(bb):

    lnex.elasticindex(conn_string='130.108.85.186:9200', index_name="photon_v1")
    #lnex.elasticindex(conn_string='localhost:9201', index_name="photon")

    return lnex.initialize(bb, augment=True)

################################################################################

if __name__ == "__main__":

    bbs = {
        "chennai": [12.74, 80.066986084, 13.2823848224, 80.3464508057],
        "louisiana": [29.4563,-93.3453,31.4521,-89.5276],
        "houston": [29.4778611958,-95.975189209,30.1463147381,-94.8889160156]
    }

    for bb in bbs:

        '''if bb not in ["chennai", "louisiana"]:
            continue'''

        init_using_elasticindex(bbs[bb])

        ########################################################################

        filename = bb+"_annotations.json"

        anns = read_annotations(filename)

        TPs_count = .0
        FPs_count = .0
        FNs_count = .0
        overlaps_count = 0

        fns = defaultdict(int)

        count = 0
        one_geolocation = .0
        all_geolocation = .0
        geo_codes_length_dist = defaultdict(int)

        out_and_amb_extracted_lns = 0

        for key in anns:

            count += 1

            # skip the development set
            if bb != "houston" and count < 500:
                continue

            tweet_lns = set()
            lnex_lns = set()
            tweet_text = ""

            for ann in anns[key]:
                if ann != "text":
                    ln = anns[key][ann]

                    tweet_lns.add(((int(ln['start_idx']), int(ln['end_idx'])),
                                        ln['type']))
                else:
                    tweet_text = anns[key][ann]
                    #print tweet_text

                    r = lnex.extract(tweet_text)

                    # how many are already disambiguated +++++++++++++++++++++++
                    for res in r:
                        if len(res[3]) < 2:
                            one_geolocation += 1

                            #if len(res[3]) == 0:
                                #print res[2]
                        else:
                            geo_codes_length_dist[len(res[3])] += 1

                        all_geolocation += 1
                    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                    lnex_lns = set([x[1] for x in r])

            #print tweet_lns, [tweet_text[x[0][0]:x[0][1]] for x in tweet_lns]
            #print lnex_lns, [tweet_text[x[0]:x[1]] for x in lnex_lns]

            # The location names of type outLoc and ambLoc that the tools
            #   should've not extracted them
            tweet_lns_not_inLocs = set([x[0] for x in tweet_lns
                                            if x[1] != 'inLoc'])

            # add all extracted lns than are of types other than inLoc as FPs
            amb_and_out_extracted = lnex_lns & tweet_lns_not_inLocs
            out_and_amb_extracted_lns += len(amb_and_out_extracted)
            FPs_count += len(amb_and_out_extracted)

            # remove LNs that are not inLoc, we already calculated their effect
            tweet_lns = set([x[0] for x in tweet_lns]) - tweet_lns_not_inLocs
            lnex_lns -= tweet_lns_not_inLocs

            # True Positives +++++++++++++++++++++++++++++++++++++++++++++++++++
            TPs = tweet_lns & lnex_lns

            TPs_count += len(TPs)

            # Left in both sets ++++++++++++++++++++++++++++++++++++++++++++++++
            tweet_lns -= TPs
            lnex_lns -= TPs

            # Find Overlapping LNs to be counted as 1/2 FPs and 1/2 FNs++
            overlaps = set()
            for x in tweet_lns:
                for y in lnex_lns:
                    if do_they_overlap(x, y):
                        overlaps.add(x)
                        overlaps.add(y)

            # count all overlapping extractions with non-inLoc as FPs
            FPs_count += len(overlaps & tweet_lns_not_inLocs)

            # count the number of overlaps that are of type inLoc as 1/2s
            overlaps = overlaps - tweet_lns_not_inLocs
            overlaps_count += len(overlaps)

            # remove the overlapping lns from lnex_lns and tweet_lns
            lnex_lns -= overlaps
            tweet_lns -= overlaps

            # False Positives ++++++++++++++++++++++++++++++++++++++++++++++++++
            # lnex_lns = all - (TPs and overlaps and !inLoc)
            FPs = lnex_lns - tweet_lns
            FPs_count += len(FPs)

            # False Negatives ++++++++++++++++++++++++++++++++++++++++++++++++++
            FNs = tweet_lns - lnex_lns
            FNs_count += len(FNs)

            '''if len(FNs) > 0:
                for x in [tweet_text[x[0]:x[1]] for x in FNs]:
                    fns[x.lower()] += 1'''

            ####################################################################
            #print TPs_count, FPs_count, FNs_count, overlaps_count
            #print "#"*100

        '''
        since we add 2 lns one from lnex_lns and one from tweet_lns if they
        overlap the equation of counting those as 1/2 FPs and 1/2 FNs is going
        to be:
            overlaps_count x
                1/2 (since we count twice) x
                    1/2 (since we want 1/2 of all the errors made)
        '''
        Precision = TPs_count/(TPs_count + FPs_count + .5 * .5 * overlaps_count)
        Recall = TPs_count/(TPs_count + FNs_count + .5 * .5 * overlaps_count)
        F_Score = (2 * Precision * Recall)/(Precision + Recall)

        percentage_disambiguated = one_geolocation/all_geolocation

        sorted_dict = OrderedDict(sorted(geo_codes_length_dist.items(), key=operator.itemgetter(0), reverse=True))

        percentage_amb_out_extracted = out_and_amb_extracted_lns/all_geolocation

        print "\t".join([bb, str(Precision), str(Recall), str(F_Score), str(percentage_disambiguated)]),"\t", percentage_amb_out_extracted

        #print json.dumps(fns)
