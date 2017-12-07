import os,time
from midiutil import mido, outport, open_midifile

midipath = './midies/'
names = os.listdir(midipath)

midies = list(filter(lambda n:True if n.lower().endswith('.mid') else False, names))

def show_info(midifile):
    print('n of tracks',len(midifile.tracks))
    print('type',midifile.type)
    print('tpb',midifile.ticks_per_beat)
    print('length of each track', [len(t) for t in midifile.tracks])

def show_all_info():
    for fn in midies:
        midifile = open_midifile(midipath+fn)
        show_info(midifile)
        del midifile

if __name__ == '__main__':
    show_all_info()
