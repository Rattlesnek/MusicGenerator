# MusicGenerator

## Preparation of dataset

1. Create statistics of songs with markers: 
    - `python stats.py [gp-dir-path] stats.json log.txt`
2. Extract certain sections from GuitarPro files:
    - `python extract_sections.py stats.json [gp-dir-path] [extracted-sections-gp-dir-path]`
3. Convert extracted GuitarPro sections to MIDI:
    - `python convert_gp_to_midi.py [extracted-sections-gp-dir-path] [midi-dir-path]`
4. Convert MIDI to .npz batches of pianoroll matrices:
    - `python convert_midi_to_npz.py [midi-dir-path] [npz-dir-path]`


