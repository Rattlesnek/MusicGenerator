import sys
import os
import pretty_midi
import numpy as np

# because I use neural network which has input of size 40
#################
fs = 20
#################


def midi_to_pianoroll(midi_name, fs):
    # open midi
    midi = pretty_midi.PrettyMIDI(midi_name)
    # create pianoroll from midi with given sample freqency
    pianoroll = midi.get_piano_roll(fs)
    # return pianoroll which contains only zeros and ones
    # number 50 was picked because it is suitable for our data (see ipynb)
    return (pianoroll >= 50).astype(float)


try:
    midi_dir = sys.argv[1]
except IndexError:
    print('Wrong arguments!')
    sys.exit(1)

cnt = 0
err_cnt = 0

for file in os.listdir(midi_dir):
    # go through dir with midi and analyze files
    cnt += 1
    midi_name = os.path.join(midi_dir, file)
    print(cnt, midi_name)

    try:
        pianoroll = midi_to_pianoroll(midi_name, fs)


    except Exception as err:
        err_cnt += 1
        print(err)