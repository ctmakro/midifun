import os,time
from midiutil import mido, get_outport, open_midifile

midipath = './midies/'
names = os.listdir(midipath)

midies = list(filter(lambda n:True if n.lower().endswith('.mid') else False, names))

list_keywords = '''Skr
Tl-
SCHUMANN - Fantasie C
SHOSTAKOVICH - Op-87
-Bth
-Br
-Deb-
-Ch
-Cle
Hero
Hung
Etude Op-08'''.split('\n')
keep_keywords = '''Chopin
CHOPIN
Chaminade
Brahms
Deb-iou
Deb-me
Hungarian'''.split('\n')
def acceptable(filename):
    # kill the files from unacceptable author.
    for s in list_keywords:
        if s in filename:
            for k in keep_keywords:
                if k in filename:
                    return True
            print(filename,'rejected due to',s)
            return False
    return True

midies = list(filter(acceptable,midies))

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
    pass
    # show_all_info()
