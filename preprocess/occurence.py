import sys
import json
import operator
import re
from collections import defaultdict
from aggregate import AggregateNames

target_markers = [
    "verse",
    "chorus",
    "intro",
    "outro",
    "solo",
    "bridge",
    "interlude",
    "pre-chorus",
    "guitar solo",
    "riff",
    # "break",
    # "couplet",
    "pre-verse",
    # "section"
]

if __name__ == "__main__":
    try:
        fname = sys.argv[1]
        selectAction = sys.argv[2]
        if selectAction not in {'--none', '--group', '--suit', '--track', '--solo'}:
            raise ValueError
        if selectAction == '--suit':
            MIN_KNOWN = int(sys.argv[3])
            MAX_UNKNOWN = int(sys.argv[4])
    except (IndexError, ValueError):
        print('Use: gpoccurence.py [stats.json] [--none/--group/--suit/--track/--solo] (num)')
        sys.exit(1)

    with open(fname, 'r') as fin:
        stats = json.load(fin)


    track_names = defaultdict(int)
    marker_names = defaultdict(int)
    songs = {}

    for filename, stat in stats.items():
        song_markers_set = set()
        song_markers_list = []
        tracks_list = []
        for measure in stat['measures'].values():
            if 'marker' in measure:
                # basic cleanse of markers
                marker = measure['marker'].lower().strip()
                # advanced cleanse and group markers            
                if selectAction in {'--group', '--suit'}:
                    marker = re.sub('[0-9]', '', marker).strip()
                    marker = re.sub('\si+', '', marker).strip()
                    marker = AggregateNames.groupMarkerNames(marker)
                # count which marker occurs how many times
                # count given marker max once per song
                if marker not in song_markers_set:
                    marker_names[marker] += 1
                    song_markers_set.add(marker)
                
                # if marker is targeted save it to given song
                if marker not in target_markers:
                    marker = 'unknown'
                song_markers_list.append(marker)

        for track in stat['tracks'].values():
            track_name = track['name'].lower().strip()
            track_name = AggregateNames.groupTrackNames(track_name)
            track_names[track_name] += 1
            
            played_perc = track['played_perc']
            tracks_list.append((track_name, played_perc))

        songs[filename] = {
            'tracks': tracks_list,
            'sequence': song_markers_list
        }



    if selectAction in {'--none', '--group'}:
        for name, value in sorted(marker_names.items(), key=lambda v: v[1], reverse=True):
            print('"', name, '" = ', value, sep='')

    elif selectAction == '--track':
        for name, value in sorted(track_names.items(), key=lambda v: v[1], reverse=True):
            print('"', name, '" = ', value, sep='')

    elif selectAction == '--suit':

        GTR_THRESH = 85

        sum_unique = 0
        sum_unknown = 0
        sum_known = 0

        suitable_cnt = 0
        suitable_with_unknown_cnt = 0
        suitable_with_guitar = 0
        suitable_all_cnt = 0
        suitable_above_gtr_tresh = 0
        gtr_played_sum_perc = 0
        gtr_played_median = []

        for sng in songs.values():
            sequence = sng['sequence']
            unknown_cnt = 0
            known_cnt = 0
            for marker in sequence:
                if marker == 'unknown':
                    unknown_cnt += 1
                else:
                    known_cnt += 1 
            
            sett = set(sequence)
            sett.discard('unknown')
            unique_markers = len(sett)            
            sum_unique += unique_markers
            sum_unknown += unknown_cnt
            sum_known += known_cnt 

            maxUnknown = False
            hasGuitar = False
            if known_cnt >= MIN_KNOWN:
                suitable_cnt += 1
                if unknown_cnt <= MAX_UNKNOWN:
                    maxUnknown = True
                    suitable_with_unknown_cnt += 1
                
                #most_played_id = None
                most_played_perc = 0
                for i, (track, played_perc) in enumerate(sng['tracks']):
                    if 'guitar' in track:
                        hasGuitar = True
                        if played_perc > most_played_perc:   
                            #most_played_id = i
                            most_played_perc = played_perc       
                
                if hasGuitar:
                    suitable_with_guitar += 1
                if hasGuitar and maxUnknown:
                    suitable_all_cnt += 1
                    gtr_played_sum_perc += most_played_perc
                    gtr_played_median.append(most_played_perc)
                    if most_played_perc >= GTR_THRESH:
                        suitable_above_gtr_tresh += 1
                
        
        print('songs w/ min', MIN_KNOWN, 'known:                ', suitable_cnt)
        print('songs w/ min', MIN_KNOWN, "known n has 'guitar': ", suitable_with_guitar)
        print('songs w/ min', MIN_KNOWN, 'known n max', MAX_UNKNOWN, 'unknown:', suitable_with_unknown_cnt)
        print('songs w/ all constraints:            ', suitable_all_cnt)
        print('avg percent of guitar time:   ', round(gtr_played_sum_perc / suitable_with_guitar, 2))
        
        gtr_played_median.sort()
        half = len(gtr_played_median) // 2
        print('median percent of guitar time:', gtr_played_median[half])
        print('songs w/ all con. n above thresh ', GTR_THRESH,'%: ', suitable_above_gtr_tresh, sep='')

        print()
        cnt_all = len(songs)
        print('avg known:  ', round(sum_known / cnt_all, 2))
        print('avg unknown:', round(sum_unknown / cnt_all, 2))
        print('avg unique: ', round(sum_unique / cnt_all, 2))
        
        # print(gtr_played_median)

        # with open('log_markers.json', 'w') as fout:
        #     json.dump(songs, fout, indent=4)

    elif selectAction == '--solo':

        lead_rythm_cnt = 0
        for sng in songs.values():
            hasLead = False
            hasRythm = False
            for i, (track, played_perc) in enumerate(sng['tracks']):
                #print(i)
                if 'lead' in track:
                    hasLead = True
                    #print('lead: ', track)
                elif 'guitar' in track:
                    hasRythm = True
                    #print('rythm:', track)
            if hasLead and hasRythm:
                lead_rythm_cnt += 1
        
        print('all:       ', len(songs))
        print('lead_rythm:', lead_rythm_cnt)
        print('perc:      ', round(lead_rythm_cnt / len(songs) *100, 2))

