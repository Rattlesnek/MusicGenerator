"""
Bachelor's thesis: Generation of guitar tracks utilizing knowledge of song structure
Author: Adam Pankuch
"""
import sys
import os
import pretty_midi
import numpy as np

#################
fs = 20 # sampling frequency of midi --> pianoroll conversion
#################
batch_size = 500 # size of the batch of pianorolls
#################
lower_len_bnd = 160 # minimal length of a pianoroll
upper_len_bnd = 600 # maximal length of a pianoroll
#################

def midi_to_pianoroll(midi_name, fs):
    """Creates pianoroll from a midi."""
    midi = pretty_midi.PrettyMIDI(midi_name)
    # create pianoroll from midi with given sample freqency
    pianoroll = midi.get_piano_roll(fs)
    # return pianoroll which contains only zeros and ones
    # number 50 was picked because it is suitable for our data
    return (pianoroll >= 50).astype(float)

def used_notes(pianoroll):
    """Finds what pitches of notes were used in the song."""
    notes_sum = np.sum(pianoroll, axis=1)
    return np.nonzero(notes_sum)[0]

def preprocess_batch(batch):
    """Sorts a batch of pianorolls."""
    return sorted(batch, key=lambda x: np.size(x, axis=1))

def save_batch(id_batch, batch, dst_dir):
    """Saves a batch of pianorolls."""
    npz_name = os.path.join(dst_dir, 'batch' + str(id_batch) + '.npz')
    # save batch of pianorolls to .npz archive for efficiency
    np.savez_compressed(npz_name, *batch)


if __name__ == "__main__":
    try:
        src_dir = sys.argv[1]
        dst_dir = sys.argv[2]
    except IndexError:
        print('Use: python convert_midi_to_npz.py [midi-dir-path] [npz-dir-path]')
        sys.exit(1)

    cnt = 0
    cnt_removed = 0
    cnt_err = 0

    id_batch = 0
    batch = []
    for file in os.listdir(src_dir):
        # go through dir with midi and convert each file to pianoroll
        cnt += 1
        midi_name = os.path.join(src_dir, file)
        print(cnt, midi_name)

        try:
            pianoroll = midi_to_pianoroll(midi_name, fs)
        except Exception as err:
            cnt_err += 1
            print(err)
            continue

        notes = used_notes(pianoroll)
        # remove songs that don't have notes or have notes out of range of guitar
        # range of notes on guitar with standard tuning 44 == E2 (lowest string), 88 == E6 (highest string 24th fret) 
        if notes.size == 0 or notes.min() < 40 or 88 < notes.max(): 
            cnt_removed += 1
            continue

        pianoroll_len = np.size(pianoroll, axis=1) 
        # remove songs that are longer or shorter then given bounds
        if pianoroll_len < lower_len_bnd or upper_len_bnd < pianoroll_len:
            cnt_removed += 1
            continue

        # add pianoroll to batch -- batch will be converted to .npz archive for efficiency
        batch.append(pianoroll)

        # if batch is large enough --> save batch
        if len(batch) == batch_size:
            id_batch += 1
            print(' -- batch', id_batch)

            batch = preprocess_batch(batch)
            save_batch(id_batch, batch, dst_dir)
            # clear batch list
            batch = []


    # if there are some pianorolls in batch left --> save batch
    if len(batch) != 0:
        print('last batch len:', len(batch))
        overflow = len(batch) % 10
        if overflow != 0:
            batch = batch[:-overflow]
        print('last batch len cut:', len(batch))

        if len(batch) != 0:
            id_batch += 1
            print(' -- batch', id_batch)
            batch = preprocess_batch(batch)
            save_batch(id_batch, batch, dst_dir)
            # clear batch list
            batch = []

    # statistics
    print('cnt', cnt)
    print('cnt_err', cnt_err)
    print('cnt_removed', cnt_removed)
