import numpy as np 


def smooth(song):
    for i in range(song.shape[0]):
        last_one = None
        for j in range(song.shape[1]):
            
            if last_one is not None and song[i, j] == 1:
                if last_one == j - 2:
                    song[i, j-1] = 1
                if last_one == j - 3:
                    song[i, j-1] = 1
                    song[i, j-2] = 1

            if song[i, j] == 1:
                last_one = j
    return song


def output_to_pianoroll(track):
    # remove 4th channels dimension
    track = np.squeeze(track)
    # transpose in order to reshape correctly
    # reshape from 3D to 2D -- where y are notes and x is time
    song = np.reshape(track.transpose(1, 0, 2), (40, -1))
    # convert to 'int' for safe comparison of numbers
    song = song.astype('int')
    # "smooth out" song
    song = smooth(song)
    # pad the song so ther its shape is (128, x) -- like a pianoroll
    pianoroll = np.pad(song, ((40, 48), (0, 0)))
    # change ones to some normal integer eg. 95
    pianoroll = np.where(pianoroll == 1, 95, pianoroll)
    return pianoroll

    