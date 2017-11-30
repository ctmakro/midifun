import mido,time
import sys
# sys.stdout.encoding = 'utf-8'
print(sys.stdout.encoding)

mido.set_backend('mido.backends.rtmidi')

outport = mido.open_output()

msg = mido.Message('note_on', note=60)
print(msg.bytes())

outport.send(msg)

# time.sleep(4)

def playfile(fn):
    from mido import MidiFile
    midifile = MidiFile(fn,charset='latin-1')
    print(len(midifile.tracks))
    print('type',midifile.type)

    for msg in midifile:
        time.sleep(msg.time)
        if not msg.is_meta:
            outport.send(msg)

        print(str(msg).encode('utf-8'))

playfile('./midies/mz_311_3.mid')
