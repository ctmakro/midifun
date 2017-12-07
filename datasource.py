# read midi files, convert into event stream format, export as query-able datasource.
import numpy as np
import os

from midiutil import mido, outport, open_midifile
from iter import midies
from events import MIDI_to_events, play_events, Event

data_filename = 'converted.npz'

def convert_all_and_save():
    streams = []
    for fn in midies:
        print('converting', fn)
        events = MIDI_to_events(fn)
        events = [e.to_integer() for e in events]
        events = np.array(events).astype('uint8')
        print('done.')
        streams.append(events)

    with open(data_filename,'wb') as f:
        # create an array object and put all the arrays into it.
        # otherwise np.asanyarray() within np.savez_compressed()
        # might make stupid mistakes
        w = streams
        arrobj = np.empty([len(w)],dtype='object') # array object
        for i in range(len(w)):
            arrobj[i] = w[i]

        np.savez_compressed(f,w=arrobj)
        print('successfully saved to',data_filename)

def load_converted():
    with open(data_filename,'rb') as f:
        loaded_w = np.load(f)
        print('successfully loaded from',data_filename)
        if hasattr(loaded_w,'items'):
            # compressed npz (newer)
            loaded_w = loaded_w['w']
    return loaded_w

def convert_if_needed():
    if os.path.exists(data_filename):
        pass
    else:
        convert_all_and_save()

convert_if_needed()
streams = load_converted()

if __name__ == '__main__':
    events = streams[np.random.choice(len(streams))]
    events = [Event.from_integer(e) for e in events]
    play_events(events)
