"""
Bachelor's thesis: Generation of guitar tracks utilizing knowledge of song structure
Author: Adam Pankuch
"""
import sys
import glob
import os.path
import json
import gputils


if __name__ == '__main__':
    try:
        gpDirPath = sys.argv[1]
        statsOutPath = sys.argv[2]
        logOutPath = sys.argv[3]
    except IndexError:
        print('Use: python stats.py [gp-dir-path] [stats.json] [log.txt]')
        sys.exit(1)

    stats = {}

    # iterate through all files and save statistics of songs with markers
    cnt_all = 0
    cnt_mark = 0
    cnt_corrupt = 0
    for filename in glob.iglob(gpDirPath + '**/*.gp*', recursive=True):
        relativeFilename = filename[len(gpDirPath):]
        if os.path.isfile(filename):
            print(cnt_all, ' ', filename)
            try:
                songStat = gputils.getSongStatistics(filename)
                if songStat is not None:
                    stats[relativeFilename] = songStat
                    cnt_mark += 1
            except:
                print('=== ERROR - corrupted file ===')
                cnt_corrupt += 1
            cnt_all += 1

    with open(statsOutPath, 'w') as fout:
        output = json.dumps(stats, indent=4)  
        fout.write(output)
    
    log = 'all:     ' + str(cnt_all) + '\n'
    log += 'mark:    ' + str(cnt_mark) + '\n'
    log += 'corrupt: ' + str(cnt_corrupt) + '\n'
    print(log)
    with open(logOutPath, 'w') as fout:
        fout.write(log)
