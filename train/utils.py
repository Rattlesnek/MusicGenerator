import pylab as plt
import numpy as np
import os

####
# Utilities class
####
class Utils:

    @classmethod
    def outputToPianoroll(cls, track):
        assert track.shape[0] == 48, 'Wrong input track dimensions!'
        # convert to 'int' for safe comparison of numbers
        track = track.astype('int')
        # pad the song so ther its shape is (128, x) -- like a pianoroll
        pianoroll = np.pad(track, ((40, 40), (0, 0)))
        # change ones to some normal integer eg. 95
        pianoroll = np.where(pianoroll == 1, 95, pianoroll)
        return pianoroll

    @classmethod
    def savePianoroll(cls, save_name, track):
        # create and save pianoroll
        pianoroll = cls.outputToPianoroll(track)
        npz_name = save_name + '.npz'
        np.savez_compressed(npz_name, pianoroll)

    @classmethod
    def plotAndSaveOutput(cls, save_name, track):
        assert track.shape[0] == 48, 'Wrong input track dimensions!'
        # plot whole output
        fig = plt.figure()
        plt.imshow(track)
        plt.savefig(save_name + '.png', dpi=1200, bbox_inches='tight')
        plt.close(fig)
        # plot shorter output
        fig = plt.figure()
        plt.imshow(track[::, :240])
        plt.savefig(save_name + '_shorter.png', dpi=1200, bbox_inches='tight')
        plt.close(fig)
