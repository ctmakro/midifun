# you have to install mido and rtmidi before running this script

import mido
from mido import MidiFile

# obtain output port
def get_outport():
    mido.set_backend('mido.backends.rtmidi')
    outport = mido.open_output()
    return outport

# open a midi file given filename
def open_midifile(fn):
    midifile = MidiFile(fn,charset='latin-1')
    return midifile

# play a file thru midi output port
def playfile(fn):
    # open the file
    midifile = open_midifile(fn)

    # display something about the file
    print(len(midifile.tracks))
    print('type',midifile.type)

    # obtain an output port
    outport = get_outport()

    import time
    # for each message in midifile
    for msg in midifile:
        # if file is associated with time delay:
        time.sleep(msg.time)

        # if file is not a meta message:
        if not msg.is_meta:
            outport.send(msg)

        # print the message
        print(str(msg).encode('utf-8'))

filename = './midies/001-Albeniz Espana Op-165 Capricho Catalan.mid'
playfile(filename)
