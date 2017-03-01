import json
from collections import defaultdict


counts = defaultdict(int)


with open('chennai_phrases.json') as data_file:
    data = json.load(data_file)

    for x in data:
        x = x.split()

        counts[len(x)]+=1


for x in counts:
    print x, counts[x]
