# given filename, return the array of events.

from events import MIDI_to_events, play_events, Event

filename = recv()
events = MIDI_to_events(filename)
send(events)
