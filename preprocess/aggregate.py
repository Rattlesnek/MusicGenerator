"""
Bachelor's thesis: Generation of guitar tracks utilizing knowledge of song structure
Author: Adam Pankuch
"""
import re

def groupMarkerNames(marker):
    """Utility function which groups markers into categories."""
    # detect chorus
    if 'chorus' in marker:
        # detect pre-chorus
        if 'pre' in marker:
            return 'pre-chorus'
        elif 'post' in marker:
            return 'post-chorus'
        else:
            return 'chorus'
    # detect chorus typo
    if 'chours' in marker:
        return 'chorus'
    # detect refrain as chorus
    if 'ref' in marker:
        return 'chorus' 
    # detect verse
    if 'vers' in marker:
        if 'pre' in marker:
            return 'pre-verse'
        else:
            return 'verse'
    # if 'section' in marker:
    #     return 'verse'
    # detect intro
    if 'intr' in marker:
        return 'intro'
    # detect interlude
    if 'interl' in marker:
        return 'interlude'
    # detect solo
    if 'solo' in marker:
        if 'piano' in marker or 'key' in marker:
            return 'piano solo'
        elif 'bass' in marker:
            return 'bass solo'
        elif 'guitar' in marker:
            return 'guitar solo'
        elif 'pre' in marker:
            return 'pre-solo'
        elif 'organ' in marker:
            return 'organ solo'
        elif 'sax' in marker:
            return 'sax solo'
        else:
            return 'solo'
    
    if 'riff' in marker:
        return 'riff'

    if 'outro' in marker or 'end' in marker or 'fin' in marker:
        return 'outro'

    return marker


def groupTrackNames(track):
    """Utility function which groups tracks into categories."""
    number = None
    match = re.search('[0-9]', track)
    number = None if match is None else match.group()

    if 'guit' in track or 'gtr' in track or 'gita' in track:
        if 'bass' in track:
            ret = 'bass' # what??
        elif 'lead' in track or 'solo' in track:
            ret = 'lead guitar'
        elif 'rythm' in track or 'rhytm' in track:
            ret = 'rythm guitar'
        elif 'acoustic' in track:
            ret = 'acoustic guitar'
        elif 'electric' in track:
            ret = 'electric guitar'
        elif 'clean' in track:
            ret = 'clean guitar'
        elif 'dist' in track:
            ret = 'distortion guitar'
        elif 'overd' in track:
            ret = 'overdrive guitar'        
        else:
            ret = 'guitar'
        return ret if number is None else ret + ' ' + number

    if 'bass' in track:
        ret = 'bass'
        return ret if number is None else ret + ' ' + number
    if 'drum' in track or 'percus' in track:
        return 'drums'
    if 'vocal' in track or 'voic' in track:
        return 'vocal'
    if 'piano' in track or 'key' in track or 'synth' in track:
        return 'piano'
    if 'batter' in track or 'bater' in track:
        return 'batterie'
    if 'bajo' in track:
        return 'bajo'
    if 'organ' in track:
        return 'organ'
    
    if 'rythm' in track:
        return 'rythm guitar'
    if 'lead' in track or 'solo' in track:
        return 'lead guitar'
    if 'chorus' in track:
        return 'chorus'
    
    if 'clean' in track:
        return 'clean guitar'
    if 'dist' in track:
        return 'distortion guitar'
    if 'overd' in track:
        return 'overdrive guitar'
    
    if 'acoustic' in track:
        return 'acoustic guitar'
    if 'electric' in track:
        return 'electric guitar'
        
    return track
