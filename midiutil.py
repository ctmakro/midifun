import mido

def get_outport():
    mido.set_backend('mido.backends.rtmidi')
    outport = mido.open_output()
    return outport

from mido import MidiFile

def open_midifile(fn):
    midifile = MidiFile(fn,charset='latin-1')
    return midifile
