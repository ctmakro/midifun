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
        # events = [e.to_integer() for e in events]
        # events = np.array(events).astype('uint8')
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

    for i in range(len(streams)):
        if i == 0:
            bigstream += streams[i]
        else:
            nf = streams[i][0]
            ls = bigstream[-1]
            if nf.category=='delay' and ls.category=='delay':
                ls.value+=nf.value
                combination_counter+=1
                bigstream += streams[i][1:]
            else:
                bigstream += streams[i]

    print('joined_bigstream:', len(bigstream))
    print('delay events conbined:', combination_counter)
    bigstream = np.array([e.to_integer()for e in bigstream]).astype('uint8')

    return bigstream

convert_if_needed()
bigstream = load_converted()

# if __name__ == '__main__':
    # events = streams[np.random.choice(len(streams))]
    # events = [Event.from_integer(e) for e in events]
    # play_events(events)
