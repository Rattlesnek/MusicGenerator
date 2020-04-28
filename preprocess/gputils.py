import guitarpro as gp
import subprocess

class GpConverter:

    class ConvertError(Exception) : pass

    def __init__(self, gpToMidiConverterPath):
        self.gpToMidiConverterPath = gpToMidiConverterPath


    def gpToMidi(self, gpPath, midiPath):
        cmd = ['mono', self.gpToMidiConverterPath, gpPath, midiPath]
        try:
            subprocess.run(cmd, check=True, timeout=2)
        except Exception as err:
            raise self.ConvertError(err)


class GpUtils:

    @staticmethod
    def extractPart(song, trackId, fromMeasure, toMeasure):
        track = song.tracks[trackId]
        measures = track.measures[fromMeasure - 1:toMeasure]
        tempo = song.tempo

        for i in range(fromMeasure - 1):
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

    @staticmethod
    def getSongStatistics(filename):
        song = gp.parse(filename)
        # test if song has markers
        hasMarkers = False
        for measure in song.measureHeaders:
            if measure.hasMarker:
                hasMarkers = True
                break
        if hasMarkers == False:
            return None

        # save important data
        stat = {
            'title' : song.title,
            'artist' : song.artist,
            'key' : str(song.key),
            'length' : len(song.measureHeaders),
            'tempoName' : song.tempoName,
            'tempo' : song.tempo,
            'tracks' : {},
            'measures' : {}
        }

        for track in song.tracks:
            play_measures = []
            # find out how many measures of given track are actually played
            for measure in track.measures:
                isPlayed = False
                for voice in measure.voices:
                    for beat in voice.beats:
                        if len(beat.notes) != 0:
                            isPlayed = True
                            break
                    if isPlayed:
                        break
                play_measures.append(isPlayed)

            stat['tracks'][track.number] = {
                'name' : track.name,
                'isSolo' : track.isSolo,
                'r' : track.color.r,
                'g' : track.color.g,
                'b' : track.color.b,
                'played_perc' : round(float(play_measures.count(True)) / len(track.measures) * 100, 2),
            }   

        # find repeat
        current_timeSig = (0, 0)
        current_length = 0
        repClosing = 0

        for measure in song.measureHeaders:
            infoCollection = {}

            new_timeSig = (measure.timeSignature.numerator,
                measure.timeSignature.denominator.value)
            if current_timeSig[0] != new_timeSig[0] or current_timeSig[1] != new_timeSig[1]:
                current_timeSig = new_timeSig
                infoCollection['time(n/d)'] = current_timeSig
            # print('time sig numerator:', measure.timeSignature.numerator, 'denominator:', measure.timeSignature.denominator.value)
            if current_length != measure.length:
                current_length = measure.length
                infoCollection['length'] = current_length
            # print('length:', measure.length)
            if measure.isRepeatOpen or repClosing == measure.number:
                repClosing = measure.repeatGroup.closings[0].number
                infoCollection['isRepeat'] = True
                infoCollection['open'] = measure.repeatGroup.openings[0].number
                infoCollection['close'] = measure.repeatGroup.closings[0].number
                # print('  open',measure.repeatGroup.openings[0].number)
                # print('  close',measure.repeatGroup.closings[0].number)
            if measure.repeatClose > 0:
                infoCollection['numRepeats'] = measure.repeatClose
                # print('  number of repetitions:', measure.repeatClose)
            if measure.hasMarker:
                infoCollection['marker'] = measure.marker.title

            # save to stat
            if infoCollection:
                stat['measures'][measure.number] = infoCollection
        
        return stat
