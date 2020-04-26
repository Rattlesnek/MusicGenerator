import guitarpro as gp
import sys
import glob
import os
import json
import smtplib
from email.message import EmailMessage


NUM_PARTS = 6
stats = {}

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def statistics(filename):
    song = gp.parse(filename)
    # test if song has markers
    hasMarkers = False
    for measure in song.measureHeaders:
        if measure.hasMarker:
            hasMarkers = True
            break
    if hasMarkers == False:
        return False

    # save important data
    stats[filename] = {
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

        # len_part = len(play_measures) // NUM_PARTS
        # part_stats = []
        # for part, i in zip(chunks(play_measures, len_part), range(NUM_PARTS)):
        #     if i == NUM_PARTS - 1:
        #         # last part -- add remain
        #         part += chunks(play_measures, len_part)
        #     part_stats.append(round(part.count(True) / len(part) * 100, 2))

        # rgb_id = (track.color.r, track.color.g, track.color.b)
        stats[filename]['tracks'][track.number] = {
            'name' : track.name,
            'isSolo' : track.isSolo,
            'r' : track.color.r,
            'g' : track.color.g,
            'b' : track.color.b,
            'played_perc' : round(float(play_measures.count(True)) / len(track.measures) * 100, 2),
            # 'part_stats' : part_stats
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
        if infoCollection:
            stats[filename]['measures'][measure.number] = infoCollection
    
    return True


def send_mail(data, log):
    msg = EmailMessage()
    msg["From"] = 'ml.stats.python@gmail.com'
    msg["Subject"] = 'Guitar Pro statistics'
    msg["To"] = 'adam.pankuch@gmail.com'
    msg.set_content("Hello,\nyour Guitar Pro statistics are ready!\n\nYours sincerely,\nPython Bot")
    msg.add_attachment(data, filename='stats.json')
    msg.add_attachment(log, filename='log.txt')

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login('ml.stats.python@gmail.com', 'Python4ever')
    server.send_message(msg)
    server.quit()


if __name__ == '__main__':
    try:
        root_dir = sys.argv[1]
        filename_out = sys.argv[2]
    except IndexError:
        print('Use: gpstats.py [gp_dir] [stat_out_file]')
        sys.exit(1)
    log = ''
    cnt_all = 0
    cnt_mark = 0
    cnt_corrupt = 0
    for filename in glob.iglob(root_dir + '**/*.gp*', recursive=True):
        filename = os.path.realpath(filename)
        if os.path.isfile(filename):
            print(cnt_all, ' ', filename)
            try:
                hasMarkers = statistics(filename)
            except:
                print('=== ERROR -- corrupted file ===')
                cnt_corrupt += 1
            if hasMarkers:
                cnt_mark += 1
            cnt_all += 1

    with open(filename_out, 'w') as fout:
        output = json.dumps(stats, indent=4)  
        fout.write(output)

    print('all:', cnt_all)
    print('mark:', cnt_mark)
    print('corrupt:', cnt_corrupt)
    
    log += 'all:     ' + str(cnt_all) + '\n'
    log += 'mark:    ' + str(cnt_mark) + '\n'
    log += 'corrupt: ' + str(cnt_corrupt) + '\n'

    with open('log.txt', 'w') as fout:
        fout.write(log)




