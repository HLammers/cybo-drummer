''' MIDI decoder library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    MIT licence:

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
    This is a further development, highly optimized for speed and memory use when integrated into Cybo-Drummer, of:
        Simple MIDI Decoder, copyright (c) 2020 diyelectromusic (Kevin), https://github.com/diyelectromusic/, https://diyelectromusic.com/'''

import micropython

import ui

_NONE                     = const(-1)

_MONITOR_MODE_MIDI_IN     = const(0)

_COMMAND_NOTE_OFF         = const(0x80)
_COMMAND_NOTE_ON          = const(0x90)
_COMMAND_PROGRAM_CHANGE   = const(0xC0)
_COMMAND_CHANNEL_PRESSURE = const(0xD0)
_SYS_QUARTER_FRAME        = const(0xF1)
_SYS_SONG_POSITION        = const(0xF2)
_SYS_SONG_SELECT          = const(0xF3)
_SYS_TUNE_REQUEST         = const(0xF6)


@micropython.viper
class MIDIDecoder:
    '''midi decoder class; initiated by _InputPort.__init__'''

    def __init__(self, id: int):
        self.id = id
        self.channel = 0
        self.command = 0
        self.sys_common_command = 0
        self.data_1 = 0

    def read(self, midi_byte: int):
        '''read, interpret and process midi byte, depending on the data calling router.route_note_on, router_note_off, router_midi_thru and/or
        router.send_to_monitor; called by _InputPort.read'''
        id = int(self.id)
        if 0x80 <= midi_byte <= 0xEF: # voice message
            self.command = midi_byte & 0xF0
            self.channel = midi_byte & 0x0F
            self.data_1 = 0
            self.data_2 = 0
            return
        if midi_byte == 0xF0 or midi_byte == 0xF7: # sysex (filtered out)
            self.command = 0
            return
        out_channel = _NONE
        out_data_1 = _NONE
        out_data_2 = _NONE
        if 0xF1 <= midi_byte <= 0xF6: # system common message
            self.command = midi_byte
            if midi_byte != _SYS_TUNE_REQUEST:
                return
            _router = ui.router
            out_command = midi_byte
        elif 0xF8 <= midi_byte <= 0xFF: # system real-time message
            _router = ui.router
            out_command = midi_byte
        else: # midi data
            command = int(self.command)
            if command == 0: # missing running status
                return
            channel = int(self.channel)
            data_1 = int(self.data_1)
            if command == _SYS_QUARTER_FRAME or command == _SYS_SONG_SELECT:
                _router = ui.router
                out_command = command
                out_data_1 = midi_byte
                self.data_1 = 0
            elif command == _COMMAND_PROGRAM_CHANGE or command == _COMMAND_CHANNEL_PRESSURE:
                _router = ui.router
                out_channel = channel
                out_command = command
                out_data_1 = midi_byte
                self.data_1 = 0
            elif data_1 == 0: # first data byte: store
                self.data_1 = midi_byte
                return
            else: # second data byte: process
                if command == _COMMAND_NOTE_OFF:
                    ui.router.route_note_off(channel, data_1, midi_byte, id)
                    out_channel = channel
                    out_command = _COMMAND_NOTE_OFF
                    out_data_1 = data_1
                    out_data_2 = midi_byte
                    self.data_1 = 0
                elif command == _COMMAND_NOTE_ON:
                    if midi_byte == 0: # velocity == 0
                        ui.router.route_note_off(channel, data_1, 64, id)
                    else:
                        ui.router.route_note_on(channel, data_1, midi_byte, id)
                    out_channel = channel
                    out_command = _COMMAND_NOTE_ON
                    out_data_1 = data_1
                    out_data_2 = midi_byte
                    self.data_1 = 0
                elif command == _SYS_SONG_POSITION:
                    out_command = _SYS_SONG_POSITION
                    out_data_1 = data_1
                    out_data_2 = midi_byte
                    self.data_1 = 0
                    self.data_2 = midi_byte
                else:
                    out_channel = channel
                    out_command = command
                    out_data_1 = data_1
                    out_data_2 = midi_byte
                    self.data_1 = 0
                    self.data_2 = midi_byte
        _router = ui.router
        _router.route_midi_thru(out_channel, out_command, out_data_1, out_data_2, id)
        if out_channel != _NONE:
            out_channel += 1
        _router.send_to_monitor(_MONITOR_MODE_MIDI_IN, id, out_channel, out_command, out_data_1, out_data_2)