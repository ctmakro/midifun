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

    bigstream = join_all_into_one(streams)

    with open(data_filename,'wb') as f:
        np.savez_compressed(f,w=bigstream)
        print('successfully saved to',data_filename)

def load_converted():
    with open(data_filename,'rb') as f:
        loaded_w = np.load(f)
        print('successfully loaded from',data_filename)
        loaded_w = loaded_w['w']
    return loaded_w

def convert_if_needed():
    if os.path.exists(data_filename):
        pass
    else:
        convert_all_and_save()

# join all streams into a big one, combining delays
def join_all_into_one(streams):
    combination_counter = 0

    bigstream = []
    for s in streams:
        bigstream += [a for a in s]

    # deal with the joinning part
    joined_bigstream = []
    laste = None
    for e in bigstream:
        curre = Event.from_integer(e)
        if laste is not None:
            if curre.category=='delay' and laste.category=='delay':
                laste.value+=curre.value
                combination_counter+=1
            else:
                joined_bigstream.append(curre)
        else:
            joined_bigstream.append(curre)

        laste = curre

    joined_bigstream = [e.to_integer() for e in joined_bigstream]

    print('joined_bigstream:', len(joined_bigstream))
    print('delay events conbined:', combination_counter)
    joined_bigstream = np.array(joined_bigstream)

    return joined_bigstream

convert_if_needed()
bigstream = load_converted()

# if __name__ == '__main__':
    # events = streams[np.random.choice(len(streams))]
    # events = [Event.from_integer(e) for e in events]
    # play_events(events)
