import sys
import os.path
import re
import json
import guitarpro as gp 
from gputils import GpUtils
from aggregate import AggregateNames

class SongStatError(Exception) : pass

def get_part_interval(song_stat, part_type):
    chorus_start_end = [] # contains starts and ends of chorus
    isChorus = False
    chorus_id = 0
    for number, measure in song_stat['measures'].items():
        if 'marker' in measure:
            # basic cleanse of markers
            marker = measure['marker'].lower().strip()
            # advanced cleanse and group markers            
            marker = re.sub('[0-9]', '', marker).strip()
            marker = re.sub('\si+', '', marker).strip()
            marker = AggregateNames.groupMarkerNames(marker)
            
            # chorus ends at this measure
            if isChorus:
                chorus_start_end.append(int(number) - 1) # where it ends
                yield chorus_start_end
                chorus_id += 1
                isChorus = False
            # chorus starts at this measure
            if marker == part_type:
                chorus_start_end = [int(number)]
                isChorus = True
    # if there is chorus at the end of the song
    if isChorus:
        chorus_start_end.append(int(number)) # where it ends
        yield chorus_start_end
        chorus_id += 1
        isChorus = False


def calc_played_percentage(track, start, end):
    play_measures = []
    for i in range(start - 1, end):
        measure = track.measures[i]
        isPlayed = False
        for voice in measure.voices:
            for beat in voice.beats:
                if len(beat.notes) != 0:
                    isPlayed = True
                    break
            if isPlayed:
                break
        play_measures.append(isPlayed)
    length = end - start + 1
    return round(float(play_measures.count(True)) / length * 100, 2)


def check_song_vs_stat(song, song_stat):
    for track_id, track in song_stat['tracks'].items():
        track_id = int(track_id) - 1
        if track['name'] != song.tracks[track_id].name:
            raise SongStatError('stat does not correspond to given song')

def calc_track_priority(adjusted_name):
    priority = 0
    if 'drums' in adjusted_name or 'batterie' in adjusted_name:
        priority = -2
    elif 'vocal' in adjusted_name:
        priority = -1
    elif 'piano' in adjusted_name:
        priority = 1
    elif 'bass' in adjusted_name:
        priority = 2
    elif 'guitar' in adjusted_name:
        priority = 3
        if 'rythm' in adjusted_name:
            priority = 4
    return priority

def find_best_guitar_track(song, song_stat, start, end):
    check_song_vs_stat(song, song_stat)

    # counting from 0 to N-1 as in pyGP
    best_track_id = None
    best_perc = 0.0
    best_priority = 0
    for track_id, track in song_stat['tracks'].items():
        track_id = int(track_id) - 1 # stats counts track_id from 1, pyGP from 0 
        adjusted_name = track['name'].lower().strip()
        adjusted_name = AggregateNames.groupTrackNames(adjusted_name)
        
        priority = calc_track_priority(adjusted_name)
        perc = calc_played_percentage(song.tracks[track_id], start, end)
        
        # print('{} {: <25}'.format(track_id, '"' + track['name'] + '"'), sep='', end='')
        # print('priority', priority, 'percento', perc)

        # i dont know wtf am i doing
        if priority < 0:
            continue
        elif best_priority > priority:
            if best_perc < 80.0 and best_perc + 20.0 < perc:
                best_priority, best_perc = priority, perc
                best_track_id = track_id
        elif best_priority == priority:
            if best_perc < perc:
                best_priority, best_perc = priority, perc
                best_track_id = track_id
        elif best_priority < priority:
            if best_perc < perc + 10.0:
                best_priority, best_perc = priority, perc
                best_track_id = track_id
        elif best_priority == 4 and priority == 3:
            if best_perc + 10.0 < perc:
                best_priority, best_perc = priority, perc
                best_track_id = track_id
    return best_track_id  


def cut_chorus(stat_name, stat, path_gp_folder, path_out_folder):
    # print('SONG', stat_name)
    chorus = next(get_part_interval(stat, 'chorus'), None)
    if chorus is None:
        return
    start, end = chorus
    # print('start_end:', start, end)

    # parse GP song
    song = gp.parse(os.path.join(path_gp_folder, stat_name))

    # find best track -- prefers guitar with most percentage played
    track_id = find_best_guitar_track(song, stat, start, end)
    if track_id is None:
        return
    # print('best track:', track_id)
    
    part = GpUtils.extractPart(song, track_id, start, end)
    
    part_name = 'chorus1_' + stat_name.replace('/', '#').replace(' ', '_')
    print(part_name)
    gp.write(part, os.path.join(path_out_folder, part_name))


if __name__ == "__main__":
    try:
        json_file = sys.argv[1]
        path_gp_folder = sys.argv[2]
        path_out_folder = sys.argv[3]
    except IndexError:
        print('Wrong arguments!')
        sys.exit(1)

    with open(json_file, 'r') as fj:
        stats = json.load(fj)

    for stat_name, stat in stats.items():
        cut_chorus(stat_name, stat, path_gp_folder, path_out_folder)
      
