import Levenshtein as lev 
import json
import sys
import os.path
import time


try:
    jfile = sys.argv[1]
except IndexError:
    print('Wrong arguments')
    sys.exit(1)

# ON / OFF
if False:
    with open(jfile, 'r') as jf:
        stats = json.load(jf)

    names = {}

    print('START')
    start = time.time()

    for i, name1 in enumerate(sorted(stats.keys())):
        name1 = os.path.basename(name1)
        names[str(i)+'#'+name1] = {}
        
        for j, name2 in enumerate(sorted(stats.keys())):
            ######### IMPORTANT CONDITION ###########
            if i < j: 
                name2 = os.path.basename(name2)
                dst = lev.distance(name1, name2)
                if dst <= 5:
                    names[str(i)+'#'+name1][str(j)+'#'+name2] = dst


    end = time.time()
    print('TIME:', end - start)


    with open('difference.json', 'w') as fw:
        json.dump(names, fw, indent=4)

else:
    with open(jfile, 'r') as jf:
        names = json.load(jf)

    definitely_sim = 0
    possibly_sim = 0
    for name, similars in names.items():
        for similar, dst in similars.items():
            if dst <= 1:
                definitely_sim += 1
                break      
            elif dst <= 3:
                possibly_sim += 1
                break
    
    print('all:             ', len(names.keys()))
    print('definitely sim:  ', definitely_sim)
    print('possibly similar:', possibly_sim)