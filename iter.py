import os

midipath = './midies/'
names = os.listdir(midipath)

midies = list(filter(lambda n:True if n.lower().endswith('.mid') else False, names))

# print(midies)

for fn in midies:
    fn = midipath+fn
    print(fn)

    from mido import MidiFile
    midifile = MidiFile(fn)

    print('n of tracks',len(midifile.tracks))
    print('type',midifile.type)
    print('tpb',midifile.ticks_per_beat)
    print([len(t) for t in midifile.tracks])

    del midifile
