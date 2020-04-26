# MusicGenerator

## Preparation of dataset

1. Create statistics of songs with markers using: 
    - python stats.py [gpDirpath] stats.json statsLog.txt
2. Analyse statistics by: 
    - python occurence.py stats.json [other options]
3. Extract certain parts of GuitarPro files:
    - python extract_parts.py~ stats.json [gpDirPath] [extractPartGpDirPath]
4. Convert GuitarPro parts to MIDI:
    - python convert_gp_to_midi.py [extractPartGpDirPath] [midiDirPath]
5. Convert MIDI to .npz batches of pianoroll matrices:
    - python convert_midi_to_npzBatch.py [midiDirPath] [npzBatchDirPath]


