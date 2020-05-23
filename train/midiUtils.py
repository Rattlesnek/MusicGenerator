"""
Bachelor's thesis: Generation of guitar tracks utilizing knowledge of song structure
Author: Adam Pankuch
"""
import pylab as plt
import numpy as np
import pretty_midi
from reverse_pianoroll import pianoroll_to_pretty_midi
from midi2audio import FluidSynth
import IPython as ipy
# !apt install fluidsynth
# !pip install midi2audio
# !pip install pretty_midi

# path to sound font .sf2 file
soundFontPath = '/content/gdrive/My Drive/Music Gen/sound_font/clean_telecaster_font.sf2'

def playMidi(midi, savePath):
    """Plays (and saves) midi.
    Note: Works only in Jupyter notebook.
    """
    synth = FluidSynth(soundFontPath)
    midi.write(savePath + '.midi')
    synth.midi_to_audio(savePath + '.midi', savePath + '.wav')
    ipy.display.display(ipy.display.Audio(savePath + '.wav'))

def joinNames(net_name, song_name):
    """Joins two names."""
    return net_name.strip().lower().replace(' ', '-') + '_' + song_name.strip().lower().replace(' ', '-')

def plotMidi(save_path, net_name, song_name, midi):
    """Plots midi as a pianoroll."""
    fig, ax = plt.subplots()
    plt.title(net_name + ' - ' + song_name)
    plt.ylabel('Pitch')
    plt.xlabel('Time')   
    plt.imshow(midi.get_piano_roll(fs=20))
    plt.axvline(x=119)
    plt.show()
    fig.savefig(save_path + joinNames(net_name, song_name) + '.png', bbox_inches = 'tight', format='png', dpi=1200)

