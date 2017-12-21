# filter out those not enjoyable.

from iter import midies # files.
import numpy as np

from midiutil import mido, get_outport, open_midifile
import time

stopflag = False
def playfile(fn, skipdelay=False):
    outport = get_outport()

    global stopflag

    midifile = open_midifile(fn)
    print(len(midifile.tracks))
    print('type',midifile.type)

    cached_delay = 0
    for msg in midifile:
        if stopflag == True:
            break

        # time.sleep(msg.time)
        cached_delay+=msg.time
        if not msg.is_meta:
            time.sleep(min(cached_delay,2 if skipdelay else 5))
            cached_delay = 0
            outport.send(msg)

        # print(str(msg).encode('utf-8'))
    del midifile

log = dict() # name -> judgement

def judge():
    global stopflag
    while 1:
        idx = np.random.choice(len(midies))
        fname = midies[idx]
        if fname in log:
            continue # skip

        print('-'*30)
        print('now trying to play',fname)
        # start a new thread playing midi. stop the thread once result is obtained.
        import threading as th
        t = th.Thread(target=playfile, args=(fname,True), daemon=True)
        stopflag = False
        t.start()

        answer = input('keep this song?[y/n]')
        if answer == 'q':
            stopflag=True
            break
        elif answer != 'n':
            print('kept.')
            log[fname] = True
        else:
            print('rejected.')
            log[fname] = False

        stopflag=True
        t.join()

import pickle
def save():
    global log
    with open('filtered_list','wb') as f:
        pickle.dump(log,f)

def load():
    global log
    with open('filtered_list','rb') as f:
        log = pickle.load(f)

def get_filtered_list():
    global log
    load()
    out = []
    for f in midies:
        if f in log:
            if log[f]==True:
                out.append(f)
    print('filter:',len(out),'songs left')
    return out

if __name__ == '__main__':
    # judge()
    pass
