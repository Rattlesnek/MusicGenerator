from mido import MidiFile, MidiTrack, Message
import numpy as np

lower_bound = 21
upper_bound = 108
note_range = upper_bound - lower_bound + 1 #includes 

samples_per_measure = 96

def note2index(note):
    return note - lower_bound

def index2note(note):
    return note + lower_bound

def ticks2samples(tick_time, ticks_per_measure):
    return tick_time * samples_per_measure / ticks_per_measure


def mid2vec(fname):
    mid = MidiFile(fname)
    ticks_per_beat = mid.ticks_per_beat # how many samples per single quarter note
    ticks_per_measure = 4 * ticks_per_beat # how many samples per single measure

    all_notes = {note_index:[] for note_index in range(note_range)}
    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        
        if i == 10:

            # upravit
            abs_time = 0
            for msg in track:
                abs_time += msg.time 
                if msg.type == 'note_on':
                    print(msg)
                    note = note2index(msg.note)
                    if msg.velocity != 0:
                        all_notes[note].append([ticks2samples(abs_time, ticks_per_measure)])
                    else:
                        all_notes[note][-1].append(ticks2samples(abs_time, ticks_per_measure))
                if msg.type == 'note_off':
                    all_notes[note][-1].append(ticks2samples(abs_time, ticks_per_measure))

    samples = []
    for i in range(int(ticks2samples(abs_time, ticks_per_measure))):
        tick_vec = np.zeros((note_range, 1), dtype=np.uint8) 
        for note in all_notes.keys():
            for start, end in all_notes[note]:
                if start <= i <= end:
                    tick_vec[note] = 1
                    break
        samples.append(tick_vec)    

    print(samples[-3:-1])
            
    print('final time ', abs_time)
    return samples


def vec2mid(samples, fname, thresh=0.5):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    ticks_per_beat = mid.ticks_per_beat
    ticks_per_measure = 4 * ticks_per_beat
    ticks_per_sample = int(ticks_per_measure / samples_per_measure)
    abs_time = 0
    last_time = 0
    last_sample  = len(samples) - 1

    for i in range(len(samples)):
        abs_time += ticks_per_sample
        curr_samp = samples[i]

        for note_index in range(curr_samp.shape[0]):
            note = index2note(note_index)
            if curr_samp[note_index,0] >= thresh and (i == 0 or samples[i-1][note_index,0] < thresh):
                delta_time = abs_time - last_time
                track.append(Message('note_on', note=note, velocity=127, time=delta_time))
                last_time = abs_time
            if curr_samp[note_index,0] >= thresh and (i == last_sample or samples[i+1][note_index,0] < thresh):
                delta_time = abs_time - last_time
                track.append(Message('note_off', note=note, velocity=127, time=delta_time))
                last_time = abs_time
    mid.save(fname)

    print('final time ', abs_time)



### TEST
vec = mid2vec('09carnivalcuckoo.mid')
vec2mid(vec, 'test.mid')



