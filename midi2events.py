# given filename, return the array of events.

from events import MIDI_to_events, play_events, Event

filename = recv()
try:
    events = MIDI_to_events(filename)
except Exception as e:
    import traceback
    traceback.print_exc()
    send(None)
else:
    send(events)
