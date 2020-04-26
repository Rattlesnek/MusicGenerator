import glob
import sys
import os
import subprocess
import json
import time

class ConvertError(Exception) : pass

def gp_to_midi(gp_name, midi_name):
    cmd = ['mono', '../other/GuitarPro-to-Midi/Convert.exe', gp_name, midi_name]
    try:
        subprocess.run(cmd, check=True, timeout=2)
    except Exception as err:
        raise ConvertError(err)


if __name__ == "__main__":
    try:
        src_dir = sys.argv[1]
        dst_dir = sys.argv[2]
        jfile = sys.argv[3]
    except IndexError:
        print('Use: python gp2midi [src_dir] [dst_dir] [json_stats]')
        sys.exit(1)


    # open json statistics
    with open(jfile, 'r') as jf:
        stats = json.load(jf)
    fname_set = set()
    for stat_fname in stats.keys():
        pathToDir, relativePathToFile = stat_fname.split('60000Tabs_ulozto/')
        fname_set.add(relativePathToFile)


    start = time.time()
    cnt = 0
    err_cnt = 0
    for gp_name in glob.iglob(src_dir + '**/*.gp*', recursive=True):
        gp_name = os.path.realpath(gp_name)
        if os.path.isfile(gp_name):
            pathToDir, relativePathToFile = gp_name.split('60000Tabs_ulozto/')
            if relativePathToFile in fname_set:
                cnt += 1
                print(cnt, gp_name)
                midi_name = os.path.join(dst_dir, relativePathToFile) + '.midi'
                try:
                    gp_to_midi(gp_name, midi_name)
                except ConvertError as err:
                    err_cnt += 1
                    print('# Error occurred')

    end = time.time()
    print('all cnt:  ', cnt)
    print('err cnt:  ', err_cnt) # error cnt was: 1431
    print('stats len:', len(stats.keys()))
    print('elapsed time:', end - start)
