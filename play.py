import mido,time

mido.set_backend('mido.backends.rtmidi')

outport = mido.open_output()

msg = mido.Message('note_on', note=60)
print(msg.bytes())

outport.send(msg)

# time.sleep(4)

def playfile(fn):
    from mido import MidiFile
    midifile = MidiFile(fn)
    print(len(midifile.tracks))
    print('type',midifile.type)

    for msg in midifile:
        time.sleep(msg.time)
        if not msg.is_meta:
            outport.send(msg)

            print(msg)

playfile('./midies/bach_846.mid')
