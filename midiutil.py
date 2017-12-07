import mido
mido.set_backend('mido.backends.rtmidi')
outport = mido.open_output()

from mido import MidiFile

def open_midifile(fn):
    midifile = MidiFile(fn,charset='latin-1')
    return midifile
