import sys
import json
import operator
from collections import defaultdict

track_names = defaultdict(int)
marker_names = defaultdict(int)

try:
    fname = sys.argv[1]
except IndexError:
    print('Use: gpoccurence.py [stats.json] [occurence.json]')
    sys.exit(1)


with open(fname, 'r') as fin:
    stats = json.load(fin)

for stat in stats.values():
    for track in stat['tracks'].values():
        track_names[track['name']] += 1
    for measure in stat['measures'].values():
        if 'marker' in measure:
            marker_names[measure['marker'].lower()] += 1

for name, value in sorted(marker_names.items(), key=lambda v: v[1], reverse=True):
    print(name, ' = ', value)
