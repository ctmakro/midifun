import os,time
from midiutil import mido, get_outport, open_midifile

midipath = './midies/'
names = os.listdir(midipath)

midies = list(filter(lambda n:True if n.lower().endswith('.mid') else False, names))

midies = [midipath+m for m in midies]

def show_info(midifile):
    print('n of tracks',len(midifile.tracks))
    print('type',midifile.type)
    print('tpb',midifile.ticks_per_beat)
    print('length of each track', [len(t) for t in midifile.tracks])

def show_all_info():
    for fn in midies:
        midifile = open_midifile(fn)
        show_info(midifile)
        del midifile

if __name__ == '__main__':
    show_all_info()
