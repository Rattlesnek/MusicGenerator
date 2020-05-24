"""
Bachelor's thesis: Generation of guitar tracks utilizing knowledge of song structure
Author: Adam Pankuch
"""
import subprocess

class GpConverter:
    """
    Guitar Pro to Midi converter.
    """

    class ConvertError(Exception) : pass

    def __init__(self, gpToMidiConverterPath):
        """Instantiates a converter.
        Path to Gp-to-midi-converter needs to be specified.
        """
        self.gpToMidiConverterPath = gpToMidiConverterPath 

    def gpToMidi(self, gpPath, midiPath):
        """Converts a guitar pro file to midi using Gp-to-midi-converter.
        In case of error -> ConvertError exception is thrown.
        """
        cmd = ['mono', self.gpToMidiConverterPath, gpPath, midiPath]
        try:
            subprocess.run(cmd, check=True, timeout=2)
        except Exception as err:
            raise self.ConvertError(err)
        