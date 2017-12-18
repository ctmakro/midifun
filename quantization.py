import math,time
import numpy as np

# we have to quantize delays and stroke velocities into integers and back.
# here we create those functions.

# generate quantization and recovery function, given splits array.
def quantizer_gen(splits):
    def quantizer(value):
        if value < splits[0]:
            return 0
        elif value > splits[len(splits)-1]:
            return len(splits)-1
        else:
            # random jitter
            for i in range(len(splits)):
                if value <= splits[i]:
                    prob = (value-splits[i-1])/(splits[i]-splits[i-1])
                    if prob > np.random.uniform():
                    # if prob > 0.5:
                        return i
                    else:
                        return i-1
            raise Exception('leaking input') # we should not be here

    def recoverer(i):
        return splits[i]

    return quantizer,recoverer

# generate the splits array, given numeric parameters.
def quantization_splits_gen(steps, bias, linfac=1., qfac=0., cfac=0.):
    splits = [cfac*n*n*n + qfac*n*n + linfac*n + bias
        for n in map(lambda x: x/steps,range(steps))
    ]
    return splits

# quantization splits of delay time length
delay_quantization_splits = quantization_splits_gen(
    steps = 8,
    bias = 0.010, # 15ms
    linfac = 0.1,
    qfac = 0,
    cfac = 0,
)

# quantization splits of stroke velocity
vel_quantization_splits = quantization_splits_gen(
    steps = 8, # should do?
    bias = 0, # starts from 0
    linfac = 100,
    qfac = 40,
)

total_notes = 128
total_octaves = int(128/12) # discard a small fraction of the notes.
remain_total_notes = total_octaves*12
octave_range = total_octaves
subnote_range = 12
def note_quantize(note):
    if note>=remain_total_notes:
        return None # fails
    else:
        octave = int(note/12)
        subnote = note % 12
        assert octave<total_octaves
        assert subnote<12
        return octave,subnote

def note_recover(octave,subnote):
    return int(octave*12+subnote)

if __name__ == '__main__':
    print('delay quantization levels')
    [print(s)for s in delay_quantization_splits]
    print('vel quantization levels')
    [print(s)for s in vel_quantization_splits]

delay_quantize,delay_recover = quantizer_gen(delay_quantization_splits)
delay_quantization_levels = len(delay_quantization_splits)

vel_quantize,vel_recover = quantizer_gen(vel_quantization_splits)
vel_quantization_levels = len(vel_quantization_splits)

if __name__ == '__main__':
    testval = 0.273
    quantized = delay_quantize(testval)
    recovered = delay_recover(quantized)
    print(testval,quantized,recovered)
