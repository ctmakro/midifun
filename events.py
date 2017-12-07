from midiutil import mido, outport, open_midifile

import time

# with CodeRegistrar, you can:
# register events and specify their range of discrete values
# encode (event, value) pair into integer
# decode integer into (event, value) pair

class CodeRegistrar:
    def __init__(self):
        self.offset_index = 0
        self.offsets = {}

    def register(self, name, length):
        self.offsets[name] = [self.offset_index, length, self.offset_index+length]
        self.offset_index += length

    def encode(self, name, value):
        o = self.offsets[name]
        if 0 <= value and value < o[1]: # o[1] be length of segment
            return o[0]+value
        else:
            raise Exception('input out of range')

    def decode(self, value):
        for name in self.offsets:
            o = self.offsets[name]
            if o[0] <= value and value < o[2]:
                return name, value-o[0]
            else:
                pass
        raise Exception('input out of range')

from quantization import delay_quantize,delay_recover,vel_quantize,vel_recover
from quantization import delay_quantization_levels, vel_quantization_levels

quantize_recover_map = {
    'note': [lambda x:x,lambda x:x],
    'delay': [delay_quantize, delay_recover],
    'velocity':[vel_quantize, lambda x:int(vel_recover(x))]
}

cr = CodeRegistrar()

cr.register('note',128)
cr.register('delay', delay_quantization_levels)
cr.register('velocity',vel_quantization_levels)

# performance event representation.
# a MIDI performance can be converted into a stream of events and back.
# each event can be represented with an integer, which fits nicely into a char-rnn model.
class Event:
    def __init__(self,category,value=None):
        self.category = category # one of [delay, note, velocity]
        self.value = value

    def __repr__(self):
        return '<{}> {}'.format(self.category, self.value)

    def to_integer(self):
        value = quantize_recover_map[self.category][0](self.value)
        assert(value is not None)
        return cr.encode(self.category, value)

    @classmethod
    def from_integer(cls,i):
        category, value = cr.decode(i)
        value = quantize_recover_map[category][1](value)
        return cls(category, value)

# from MIDI file to array of events
def MIDI_to_events(fn): # given midi filename
    midifile = open_midifile(fn)
    events = []

    def get_last_event():
        nonlocal events
        if len(events)>0:
            return events[len(events)-1]
        else:
            return Event('null')

    for msg in midifile:
        if msg.time>0: # accumulate delay onto last delay event. ignore if delay is zero.
            le = get_last_event()
            if le.category == 'delay':
                le.value += msg.time
            else:
                events.append(Event('delay',msg.time))

        # time.sleep(msg.time)
        if not msg.is_meta:
            # outport.send(msg)
            if msg.type == 'note_on':
                events.append(Event('note', msg.note))
                events.append(Event('velocity', msg.velocity))
            if msg.type == 'note_off':
                events.append(Event('note', msg.note))
                events.append(Event('velocity', 0))

    print('got {} events'.format(len(events)))
    return events

# given an array of events, play them out loud
def play_events(events,speed=1.):
    selected = 0
    for event in events:
        if event.category=='delay':
            # test quantization
            # event.value = delay_recover(delay_quantize(event.value))
            delay = event.value
            time.sleep(delay/speed)
        elif event.category=='note':
            selected = event.value
        elif event.category=='velocity':
            # event.value = int(vel_recover(vel_quantize(event.value)))
            msg = mido.Message('note_on', note=selected, velocity=event.value)
            outport.send(msg)
        else:
            # print(event)
            raise NotImplementedError('unknown event')
        print(event)
    return

if __name__ == '__main__':
    events = MIDI_to_events('./midies/bach_846.mid')
    # quantize and recover
    events = [Event.from_integer(e.to_integer()) for e in events]
    play_events(events,speed=2)