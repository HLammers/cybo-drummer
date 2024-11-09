''' MIDI ports library for Cybo-Drummer - Humanize Those Drum Computers!
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
    
    Some minor concepts of this code are inspired by:
        Simple MIDI Multi-RX-TX Router, copyright (c) 2023 diyelectromusic (Kevin),
        https://github.com/diyelectromusic/, https://diyelectromusic.com/
    PIO code is taken from Simple MIDI Multi-RX-TX Router, which took it from:
        https://github.com/micropython/micropython/blob/master/examples/rp2/pio_uart_rx.py
        https://github.com/micropython/micropython/blob/master/examples/rp2/pio_uart_tx.py'''

import micropython
import machine
import rp2
import struct

from midi_decoder import MIDIDecoder
from midi_encoder import MIDIEncoder

_NONE         = const(-1)

_UART_BAUD    = const(31_250)

_PORT_IS_PIO  = const(0)
_PORT_ID      = const(1)
_PORT_PIN     = const(2)

#          _PORT_IS_PIO, _PORT_ID, _PORT_PIN
_INPUT_PORTS  = ((False,    0,     None),
                 (False,    1,     None),
                 (True,     0,     6),
                 (True,     1,     7),
                 (True,     2,     8),
                 (True,     3,     9))
_OUTPUT_PORTS = ((False,    0,     None),
                 (False,    1,     None),
                 (True,     4,     10),
                 (True,     5,     11),
                 (True,     6,     12),
                 (True,     7,     13))

class MIDIPorts:
    '''midi ports handling class; initiated once by router.__init__'''

    def __init__(self, thread_lock) -> None:
        self.thread_lock = thread_lock
        self.hardware_uarts = {}
        self.input_ports = []
        self.output_ports = []

    def load(self) -> None:
        '''load and initiate all midi input and output ports; called by router.__init__'''
        if not self.thread_lock.locked:
            self.thread_lock.acquire()
        self.hardware_uarts.clear()
        ports = []
        for port in _INPUT_PORTS:
            if not port[_PORT_IS_PIO]:
                ports.append(port[_PORT_ID])
        for port in _OUTPUT_PORTS:
            if not port[_PORT_IS_PIO]:
                ports.append(port[_PORT_ID])
        for port in set(ports):
            self.hardware_uarts[port] = machine.UART(port, _UART_BAUD)
        for i, port in enumerate(_INPUT_PORTS):
            port = _InputPort(i, port[_PORT_IS_PIO], port[_PORT_ID], port[_PORT_PIN], self.hardware_uarts) # type: ignore
            self.input_ports.append(port)
        for i, port in enumerate(_OUTPUT_PORTS):
            port = _OutputPort(i, port[_PORT_IS_PIO], port[_PORT_ID], port[_PORT_PIN], self.hardware_uarts) # type: ignore
            self.output_ports.append(port)

    def delete(self) -> None:
        for port in self.input_ports:
            port.delete()
        for port in self.output_ports:
            port.delete()
        del self.hardware_uarts
        del self.input_ports
        del self.output_ports

class _InputPort:
    '''input port handling class; initiated by MidiPorts.load'''

    def __init__(self, id: int, is_pio: bool, uart_id: int, pin: int, hardware_uarts) -> None:
        self.is_pio = is_pio
        if is_pio:
            _pin = machine.Pin(pin)
            self.pio_uart = rp2.StateMachine(uart_id, uart_rx, freq=8 * _UART_BAUD, in_base=_pin, jmp_pin=_pin)
            self.pio_uart.active(1)
        else:
            self.hardware_uart = hardware_uarts[uart_id]
        self.midi_decoder = MIDIDecoder(id)

    @micropython.viper
    def process(self):
        '''read data and send it to midi decoder if new data is available; called by main.py: second_thread'''
        if bool(self.is_pio):
            _uart = self.pio_uart
            if bool(_uart.rx_fifo()):
                midi_byte = uint(_uart.get()) >> 24 # type: ignore
                self.midi_decoder.read(midi_byte)
        else:
            _uart = self.hardware_uart
            if _uart.any():
                midi_byte = uint(_uart.read(1)[0]) # type: ignore
                self.midi_decoder.read(midi_byte)

    def delete(self):
        if self.is_pio:
            self.pio_uart.active(0)
        else:
            self.hardware_uart.deinit()

class _OutputPort:
    '''output port handling class; initiated by MidiPorts.load'''

    def __init__(self, id, is_pio: bool, uart_id: int, pin: int, hardware_uarts) -> None:
        self.is_pio = is_pio
        if is_pio:
            _pin = machine.Pin(pin)
            self.pio_uart = rp2.StateMachine(uart_id, uart_tx, freq=8 * _UART_BAUD, sideset_base=_pin, out_base=_pin)
            self.pio_uart.active(1)
            self.midi_encoder = MIDIEncoder(id, self.pio_midi_send)
        else:
            self.hardware_uart = hardware_uarts[uart_id]
            self.midi_encoder = MIDIEncoder(id, self.hardware_midi_send)

    def hardware_midi_send(self, byte_0: int, byte_1: int, byte_2: int) -> None:
        '''send midi data to hardware uart port; called by MidiEncoder.midi_send (callback_midi_send)'''
        if byte_1 == _NONE:
            self.hardware_uart.write(struct.pack('b', byte_0))
        elif byte_2 == _NONE:
            self.hardware_uart.write(struct.pack('bb', byte_0, byte_1))
        else:
            self.hardware_uart.write(struct.pack('bbb', byte_0, byte_1, byte_2))

    def pio_midi_send(self, byte_0: int, byte_1: int, byte_2: int) -> None:
        '''send midi data to pio uart port; called by MidiEncoder.midi_send (callback_midi_send)'''
        self.pio_uart.put(byte_0)
        if byte_1 != _NONE:
            self.pio_uart.put(byte_1)
        if byte_2 != _NONE:
            self.pio_uart.put(byte_2)

    def delete(self):
        if self.is_pio:
            self.pio_uart.active(0)
        else:
            self.hardware_uart.deinit()

@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_RIGHT)
def uart_rx():
    '''pio uart rx routine used for midi input'''
    label("start")             # type: ignore
    wait(0, pin, 0)            # type: ignore
    set(x, 7)             [10] # type: ignore
    label("rbitloop")          # type: ignore
    in_(pins, 1)               # type: ignore
    jmp(x_dec, "rbitloop") [6] # type: ignore
    jmp(pin, "good_stop")      # type: ignore
    wait(1, pin, 0)            # type: ignore
    jmp("start")               # type: ignore
    label("good_stop")         # type: ignore
    push(block)                # type: ignore

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_HIGH, out_init=rp2.PIO.OUT_HIGH, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def uart_tx():
    '''pio uart tx routine used for midi output (8 cycles long)'''
    pull()    .side(1)     [7] # type: ignore
    set(x, 7) .side(0)     [7] # type: ignore
    label("tbitloop")          # type: ignore
    out(pins, 1)               # type: ignore
    jmp(x_dec, "tbitloop") [6] # type: ignore