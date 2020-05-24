"""
Bachelor's thesis: Generation of guitar tracks utilizing knowledge of song structure
Author: Adam Pankuch
"""
import sys
import os.path
from gpconverter import GpConverter

gpToMidiConverterPath = "../other/GuitarPro-to-Midi/Convert.exe"

if __name__ == "__main__":
    try:
        src_dir = sys.argv[1]
        dst_dir = sys.argv[2]
    except IndexError:
        print('Use: python convert_gp_to_midi.py [gp-dir-path] [midi-dir-path]')
        sys.exit(1)

    # create converter
    converter = GpConverter(gpToMidiConverterPath)

    # iterate through all files in gp-directory
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
        
        # convert Guitar Pro to Midi
        try:
            converter.gpToMidi(gp_name, midi_name)
        except GpConverter.ConvertError as err:
            print('# Error conversion:', err)
            err_cnt += 1

    print('cnt', cnt)
    print('err_cnt', err_cnt)
