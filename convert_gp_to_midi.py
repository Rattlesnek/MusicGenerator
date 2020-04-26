import sys
import os.path
from gputils import GpConverter

gpToMidiConverterPath = "../other/GuitarPro-to-Midi/Convert.exe"
converter = GpConverter(gpToMidiConverterPath)

try:
    src_dir = sys.argv[1]
    dst_dir = sys.argv[2]
except IndexError:
    print('Wrong Arguments!')
    sys.exit(1)

cnt = 0
err_cnt = 0
for file in os.listdir(src_dir):
    cnt += 1
    gp_name = os.path.join(src_dir, file)
    midi_name = os.path.join(dst_dir, file) + '.midi'

    print(midi_name)
    if file + '.midi' in os.listdir(dst_dir):
        print('... continue')
        continue

    try:
        converter.gpToMidi(gp_name, midi_name)
    except GpConverter.ConvertError as err:
        print('# Error conversion:', err)
        err_cnt += 1

print('cnt', cnt)
print('err_cnt', err_cnt)
