import time
import sys
# sys.stdout.encoding = 'utf-8'
print(sys.stdout.encoding)

from midiutil import mido, get_outport, open_midifile

outport = get_outport()

def playfile(fn):
    midifile = open_midifile(fn)
    print(len(midifile.tracks))
    print('type',midifile.type)

    for msg in midifile:
        time.sleep(msg.time)
        if not msg.is_meta:
            outport.send(msg)

        print(str(msg).encode('utf-8'))

playfile('midies/alb_esp1.mid')
playfile('midies/Albeniz Espana (Spain) Op-165 Capricho Catalan.mid')
