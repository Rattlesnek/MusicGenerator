import os
import sys
import glob

try:
    src_dir = sys.argv[1]
    dst_dir = sys.argv[2]
except IndexError:
    print('Wrong arguments')
    sys.exit(1)

for subdir, dirs, files in os.walk(src_dir):
    subdir = subdir.replace(src_dir, '')
    #print(os.path.join(dst_dir, subdir))
    try:
        os.makedirs(os.path.join(dst_dir, subdir))
    except Exception as err:
        print(err)



