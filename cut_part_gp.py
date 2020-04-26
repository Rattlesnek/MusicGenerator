import sys
import guitarpro as gp


def cut_part_guitarpro(song, track_id, from_measure, to_measure):
    track = song.tracks[track_id]
    measures = track.measures[from_measure - 1:to_measure]
    tempo = song.tempo

    for i in range(from_measure-1):
        measure = track.measures[i]
        for voice in measure.voices:
            for beat in voice.beats:
                try:
                    if beat.effect.mixTableChange.tempo.value != tempo:
                        tempo = beat.effect.mixTableChange.tempo.value
                except AttributeError:
                    pass

    song_part = gp.Song()
    song_part.tracks = [gp.Track(song, measures=measures)]
    song_part.tempo = tempo
    return song_part


if __name__ == "__main__":
    try:
        fin = sys.argv[1]
        fout = sys.argv[2]
    except IndexError:
        print('Wrong arguments!')
        sys.exit(1)

    original = gp.parse(fin)

    song_part = cut_part_guitarpro(original, 1, 2, 3)

    gp.write(song_part, fout)

