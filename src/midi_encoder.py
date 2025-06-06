''' MIDI encoder library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    MIT licence:

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'''

import micropython

import main_loops as ml

_NONE                  = const(-1)

_MONITOR_MODE_MIDI_OUT = const(1)

_COMMAND_NOTE_OFF      = const(0x80)
_COMMAND_NOTE_ON       = const(0x90)

_NOTE_OFF_VELOCITY     = const(64)

@micropython.viper
class MIDIEncoder:
    '''midi encoder class; initiated by _OutputPort.__init__'''

    def __init__(self, id, callback_midi_send):
        self.id = id
        self.callback_midi_send = callback_midi_send
        self.vel_0_note_off = True
        self.running_status = True
        self.status_byte = -1

    def set(self, vel_0_note_off: bool, running_status: bool):
        '''set device settings; called by router.update'''
        self.vel_0_note_off = vel_0_note_off
        self.running_status = running_status

    def note_on(self, channel: int, note: int, velocity: int):
        '''generate note on message and send it to midi and monitor; called by router.route_note_on'''
        self.midi_send(_COMMAND_NOTE_ON, channel, note, velocity)
        ml.router.send_to_monitor(_MONITOR_MODE_MIDI_OUT, self.id, channel, command=_COMMAND_NOTE_ON, data_1=note, data_2=velocity)

    def note_off(self, channel: int, note: int):
        '''generate note off message and send it to midi and monitor; called by router.route_note_on, router.route_note_off and
        router._all_notes_off'''
        if bool(self.vel_0_note_off):
            self.midi_send(_COMMAND_NOTE_ON, channel, note, 0)
            ml.router.send_to_monitor(_MONITOR_MODE_MIDI_OUT, self.id, channel, command=_COMMAND_NOTE_ON, data_1=note, data_2=0)
        else:
            self.midi_send(_COMMAND_NOTE_OFF, channel, note, _NOTE_OFF_VELOCITY)
            ml.router.send_to_monitor(_MONITOR_MODE_MIDI_OUT, self.id, channel,
                                      command=_COMMAND_NOTE_OFF, data_1=note, data_2=_NOTE_OFF_VELOCITY)

    def midi_send(self, command: int, channel: int, data_1: int, data_2: int):
        '''send midi message, applying running status (unless disabled); called by note_on, note_off, router.update and
        router.route_midi_thru'''
        status_byte = command if command == _NONE else command + channel
        if not bool(self.running_status):
            running_status = False
        elif 0x80 <= status_byte <= 0xEF:
            running_status = status_byte == int(self.status_byte)
            if not running_status:
                self.status_byte = running_status
        elif 0xF0 <= status_byte <= 0xF7:
            running_status = False
            self.status_byte = _NONE
        elif 0xF8 <= status_byte <= 0xFF:
            running_status = False
        if running_status:
            byte_0 = data_1
            byte_1 = data_2
            byte_2 = _NONE
        else:
            byte_0 = status_byte
            byte_1 = data_1
            byte_2 = data_2
        self.callback_midi_send(byte_0, byte_1, byte_2)