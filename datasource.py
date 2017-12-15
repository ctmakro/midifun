# read midi files, convert into event stream format, export as query-able datasource.
import numpy as np
import os

from midiutil import mido, outport, open_midifile
from iter import midies # filenames of all midi files
from events import MIDI_to_events, play_events, Event

data_filename = 'converted.npz'

def convert_all_and_save():
    # from midies to streams of events

    streams = []

    from thready import amap
    def process(fn):
    # for fn in midies:
        print('converting', fn)
        events = MIDI_to_events(fn)
        # events = [e.to_integer() for e in events]
        # events = np.array(events).astype('uint8')
        print('done.')
        # streams.append(events)
        return events

    result = amap(process, midies)
    streams = [result[i]for i in result]

    # join into one
    print('joining...')
    bigstream = join_all_into_one(streams)

    # chop delays
    print('chopping delays...')
    bigstream = chop_delay(bigstream)

    # quantization
    print('quantization...')
    bigstream = np.array([e.to_integer()for e in bigstream]).astype('uint8')

    print('saving...')
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

# given a stream of events, chop the delay into shorter segments.
def chop_delay(stream):
    buf = []
    maxdelay = 3.0
    maxchopped = 0.0975
    for event in stream:
        value = event.value
        category = event.category
        if category=='delay':
            if value>maxdelay:
                value=maxdelay
            while True:
                if value>maxchopped:
                    value-=maxchopped
                    buf.append(Event('delay',maxchopped))
                else:
                    buf.append(Event('delay',value))
                    break
        else:
            buf.append(event)

    return buf

# join streams of events into a big stream, combining delays
def join_all_into_one(streams):
    combination_counter = 0
    bigstream = []

    for i in range(len(streams)):
        if i == 0:
            bigstream += streams[i]
        else:
            nf = streams[i][0] # first event of incoming stream
            ls = bigstream[-1] # last event of bigstream

            # if both events are of type delay
            if nf.category=='delay' and ls.category=='delay':
                ls.value+=nf.value
                combination_counter+=1
                bigstream += streams[i][1:]
            else:
                bigstream += streams[i]

    print('joined_bigstream:', len(bigstream))
    print('delay events conbined:', combination_counter)

    return bigstream

convert_if_needed()
bigstream = load_converted()

if __name__ == '__main__':
    indice = np.random.choice(len(bigstream)-2000)
    events = bigstream[indice:indice+1024]
    events = [Event.from_integer(e) for e in events]
    play_events(events)
