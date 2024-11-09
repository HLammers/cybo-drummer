''' Display library for Cybo-Drummer - Humanize Those Drum Computers!
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
    
    This library is highly optimized for speed and memory use when integrated into Cybo-Drummer. The class ‘ILI9225’ started off as an
    adaptation of:
        RaspberryPiPicoGFX, copyright (c) Michael Minor, https://github.com/9MMMinor/RaspberryPiPicoGFX/
    The class ‘Font’ is a simplified and highly optimized version of exFBfont, copyright (c) Owen Carter,
        https://github.com/easytarget/microPyEZfonts/blob/main/ezFBfont.py, which in turn is a reworked version of the class ‘Writer’,
        copyright (c) 2019-2021 Peter Hinch, https://github.com/peterhinch/micropython-font-to-py'''

import micropython
import builtins
import time
import framebuf
from machine import Pin, SPI

if __debug__: import screen_log

_DISPLAY_WIDTH           = const(220)
_DISPLAY_HEIGHT          = const(176)

_MAX_BUFFER_SIZE         = const(3824) # 1/20 screen
# _MAX_BUFFER_SIZE         = const(7744) # 1/10 screen
# _MAX_BUFFER_SIZE         = const(15488) # 1/5 screen
# _MAX_BUFFER_SIZE         = const(19360) # 1/4 screen
# _MAX_BUFFER_SIZE         = const(30976) # 2/5 screen
# _MAX_BUFFER_SIZE         = const(38720) # 1/2 screen
# _MAX_BUFFER_SIZE         = const(77440) # full screen

_BOTTOM_UP_R2L           = const(1)

# ILI9225 LCD Registers
_DRIVER_OUTPUT_CTRL      = const(0x01)  # Driver Output Control
_LCD_AC_DRIVING_CTRL     = const(0x02)  # LCD AC Driving Control
_ENTRY_MODE              = const(0x03)  # Entry Mode
_DISP_CTRL1              = const(0x07)  # Display Control 1
_BLANK_PERIOD_CTRL1      = const(0x08)  # Blank Period Control
_FRAME_CYCLE_CTRL        = const(0x0B)  # Frame Cycle Control
_INTERFACE_CTRL          = const(0x0C)  # Interface Control
_OSC_CTRL                = const(0x0F)  # Osc Control
_POWER_CTRL1             = const(0x10)  # Power Control 1
_POWER_CTRL2             = const(0x11)  # Power Control 2
_POWER_CTRL3             = const(0x12)  # Power Control 3
_POWER_CTRL4             = const(0x13)  # Power Control 4
_POWER_CTRL5             = const(0x14)  # Power Control 5
_VCI_RECYCLING           = const(0x15)  # VCI Recycling
_RAM_ADDR_SET1           = const(0x20)  # Horizontal GRAM Address Set
_RAM_ADDR_SET2           = const(0x21)  # Vertical GRAM Address Set
_GRAM_DATA_REG           = const(0x22)  # GRAM Data Register
_GATE_SCAN_CTRL          = const(0x30)  # Gate Scan Control Register
_VERTICAL_SCROLL_CTRL1   = const(0x31)  # Vertical Scroll Control 1 Register
_VERTICAL_SCROLL_CTRL2   = const(0x32)  # Vertical Scroll Control 2 Register
_VERTICAL_SCROLL_CTRL3   = const(0x33)  # Vertical Scroll Control 3 Register
_PARTIAL_DRIVING_POS1    = const(0x34)  # Partial Driving Position 1 Register
_PARTIAL_DRIVING_POS2    = const(0x35)  # Partial Driving Position 2 Register
_HORIZONTAL_WINDOW_ADDR1 = const(0x36)  # Horizontal Address Start Position
_HORIZONTAL_WINDOW_ADDR2 = const(0x37)  # Horizontal Address End Position
_VERTICAL_WINDOW_ADDR1   = const(0x38)  # Vertical Address Start Position
_VERTICAL_WINDOW_ADDR2   = const(0x39)  # Vertical Address End Position
_GAMMA_CTRL1             = const(0x50)  # Gamma Control 1
_GAMMA_CTRL2             = const(0x51)  # Gamma Control 2
_GAMMA_CTRL3             = const(0x52)  # Gamma Control 3
_GAMMA_CTRL4             = const(0x53)  # Gamma Control 4
_GAMMA_CTRL5             = const(0x54)  # Gamma Control 5
_GAMMA_CTRL6             = const(0x55)  # Gamma Control 6
_GAMMA_CTRL7             = const(0x56)  # Gamma Control 7
_GAMMA_CTRL8             = const(0x57)  # Gamma Control 8
_GAMMA_CTRL9             = const(0x58)  # Gamma Control 9
_GAMMA_CTRL10            = const(0x59)  # Gamma Control 10

_COLOR_LIGHT             = const(0xD9CD) # 0xCDD9 light purple grey

_ALIGN_LEFT              = const(0)
_ALIGN_CENTRE            = const(1)
# _ALIGN_RIGHT             = const(2)

# global variables
spi: SPI
cs: Pin
dc: Pin
rst: Pin
backlight: Pin
byte_buffer = memoryview(bytearray(_MAX_BUFFER_SIZE))

class ILI9225():
    '''screen class providing low level interaction with display; initiated once by display.__init__'''

    @micropython.native
    def __init__(self, spi_instance: SPI, cs_pin: Pin, dc_pin: Pin, rst_pin: Pin, backlight_pin: Pin, orientation: int = 0) -> None:
        global spi, cs, dc, rst, backlight
        spi = spi_instance
        cs = cs_pin
        dc = dc_pin
        rst = rst_pin
        backlight = backlight_pin
        self._orientation = orientation
        backlight_pin.off()
        self.enable_write = cs_pin.low
        self.disable_write = cs_pin.high
        rst_pin.init(rst_pin.OUT, value=0)
        dc_pin.init(dc_pin.OUT, value=0)
        cs_pin.init(dc_pin.OUT, value=1)
        self._reset()
        self._setup()
        self._clear()
        backlight_pin.on()

    @micropython.viper
    def set_display(self, flag: bool):
        '''turn display on or off (excluding backlight); called by ui.check_sleep_time_out and ui._wake_up'''
        reg_buf = bytearray(2); data_buf = bytearray(2); data_buf_0x000 = bytearray(2)
        _write = spi.write; _cs = cs; _dc_low = dc.low; _dc_high = dc.high; _cs.low()
        reg_buf[1] = 0xFF; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        if flag:
            reg_buf[1] = _POWER_CTRL1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
            time.sleep_ms(50)
            reg_buf[1] = _DISP_CTRL1; data_buf[0] = 0x10; data_buf[1] = 0x17; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
            time.sleep_ms(200)
            backlight.on()
        else:
            backlight.off()
            reg_buf[1] = _DISP_CTRL1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
            time.sleep_ms(50)
            reg_buf[1] = _POWER_CTRL1; data_buf[0] = 0x00; data_buf[1] = 0x03
            _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
            time.sleep_ms(200)
        _cs.high()

    @micropython.viper
    def fill_rect(self, x: int, y: int, w: int, h: int, color: int):
        '''draw a filled rectangle; called by self._clear ui_blocks: *.draw and _Monitor.draw'''
        if __debug__: screen_log.add_fill_rect(x, y, w, h, color)
        buffer_length_int = 2 * int(w) * int(h)
        n = 0 - ((0 - buffer_length_int) // _MAX_BUFFER_SIZE)
        while h % n > 0 and (h // n + 1) * w * 2 > _MAX_BUFFER_SIZE:
            n += 1
        if n == 0:
            n = 1
        base = h // n
        threshold = h % n
        rows = bytearray(n)
        i = 0
        while i < n:
            rows[i] = base + (1 if i < threshold else 0)
            i += 1
        y0 = y
        y1 = y - 1
        x1 = x + w - 1
        _byte_buffer = byte_buffer; _int = builtins.int
        buffer = framebuf.FrameBuffer(_byte_buffer, w, _int(rows[0]), framebuf.RGB565)
        buffer.fill(color)
        _write = spi.write; _cs = cs; _dc_high = dc.high; _set_window = self._set_window
        _cs.low()
        for row_h in rows:
            y1 += int(row_h)
            _set_window(x, y0, x1, y1); _dc_high(); _write(_byte_buffer[_int(0):_int(w * int(row_h) * 2)])
            y0 += int(row_h)
        _cs.high()

    @micropython.viper
    def draw_frame_buffer(self, x: int, y: int, w: int, h: int, back_color: int, fore_color: int, frame_buffer):
        '''draw frame buffer to screen; called by ui_blocks: *.draw, TextEdit._draw_input_text and TextEdit._draw_selection'''
        buffer_length_int = 2 * w * h
        n = 0 - ((0 - buffer_length_int) // _MAX_BUFFER_SIZE)
        while h % n > 0 and (h // n + 1) * w * 2 > _MAX_BUFFER_SIZE:
            n += 1
        if n == 0:
            n = 1
        base = h // n
        threshold = h % n
        rows = bytearray(n)
        i = 0
        while i < n:
            rows[i] = base + (1 if i < threshold else 0)
            i += 1
        segment_y = 0
        window_x1 = x + w - 1
        window_y1 = y - 1
        _byte_buffer = byte_buffer; _int = builtins.int; _write = spi.write; _cs = cs; _dc_high = dc.high; _set_window = self._set_window
        _buffer = framebuf.FrameBuffer(_byte_buffer, w, _int(rows[0]), framebuf.RGB565)
        _fill = _buffer.fill
        _src_pixel = frame_buffer.pixel; _dst_pixel = _buffer.pixel
        if __debug__:
            _screen_log_set_window = screen_log.set_window
            _screen_log_start_window_write = screen_log.start_window_write
            _screen_log_add_to_window_row = screen_log.add_to_window_row
            _screen_log_write_window_row = screen_log.write_window_row
            _screen_log_finish_window_write = screen_log.finish_window_write
        _cs.low()
        for row_h in rows:
            window_y1 += int(row_h)
            _set_window(x, segment_y + y, window_x1, window_y1)
            _fill(back_color)
            if __debug__:
                _screen_log_set_window(x, segment_y + y, window_x1 - x + 1, window_y1 - segment_y - y + 1)
                capture = _screen_log_start_window_write(back_color, fore_color)
            yy = 0
            while yy < int(row_h):
                xx = 0
                while xx < w:
                    if __debug__:
                        pixel_set = _src_pixel(xx, segment_y + yy)
                        if pixel_set: _dst_pixel(xx, yy, fore_color)
                        if capture: _screen_log_add_to_window_row(pixel_set)
                    else:
                        if _src_pixel(xx, segment_y + yy): _dst_pixel(xx, yy, fore_color)
                    xx += 1
                yy += 1
                if __debug__: _screen_log_write_window_row()
            if __debug__: _screen_log_finish_window_write()
            _dc_high(); _write(_byte_buffer[_int(0):_int(w * int(row_h) * 2)])
            segment_y += int(row_h)
        _cs.high()
        # window_x1 = x + w - 1
        # window_y1 = y + h -1
        # _byte_buffer = byte_buffer; _int = builtins.int; _write = spi.write; _cs = cs; _dc_high = dc.high; _set_window = self._set_window
        # _buffer = framebuf.FrameBuffer(_byte_buffer, w, h, framebuf.RGB565)
        # _fill = _buffer.fill
        # _cs.low()
        # _set_window(x, y, window_x1, window_y1)
        # _fill(back_color)
        # _palette = palette
        # _palette_pixel = _palette.pixel
        # _palette_pixel(0, 0, back_color)
        # _palette_pixel(1, 0, fore_color)
        # _buffer.blit(frame_buffer, 0, 0, back_color, _palette)
        # _dc_high(); _write(_byte_buffer[_int(0):_int(w * h * 2)])
        # _cs.high()

    def delete(self):
        global byte_buffer
        del byte_buffer

    @micropython.viper
    def _setup(self):
        '''screen set up routine; called by self.__init__'''
        reg_buf = bytearray(2); data_buf = bytearray(2); data_buf_0x000 = bytearray(2)
        _write = spi.write; _cs = cs; _dc_low = dc.low; _dc_high = dc.high
        _cs.low()
        reg_buf[1] = _POWER_CTRL1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # set SAP, DSTB, STB
        reg_buf[1] = _POWER_CTRL2; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # set APON, PON, AON, VCI1EN, VC
        reg_buf[1] = _POWER_CTRL3; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # set BT, DC1, DC2, DC3
        reg_buf[1] = _POWER_CTRL4; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # set GVDD
        reg_buf[1] = _POWER_CTRL5; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # set VCOMH/VCOML voltage
        reg_buf[1] = _POWER_CTRL2; data_buf[0] = 0x00; data_buf[1] = 0x18 # set APON, PON, AON, VCI1EN, VC
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _POWER_CTRL3; data_buf[0] = 0x11; data_buf[1] = 0x21 # set BT, DC1, DC2, DC3
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _POWER_CTRL4; data_buf[0] = 0x00; data_buf[1] = 0x66 # set GVDD
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _POWER_CTRL5; data_buf[0] = 0x5F; data_buf[1] = 0x60 # set VCOMH/VCOML voltage
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _POWER_CTRL1; data_buf[0] = 0x0A; data_buf[1] = 0x00 # set SAP, DSTB, STB
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(10)
        reg_buf[1] = _POWER_CTRL2; data_buf[0] = 0x10; data_buf[1] = 0x38 # set APON,PON,AON,VCI1EN,VC
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(50)
        reg_buf[1] = _DRIVER_OUTPUT_CTRL; data_buf[0] = 0x03; data_buf[1] = 0x1C # set display line number and display direction
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(10)
        reg_buf[1] = _LCD_AC_DRIVING_CTRL; data_buf[0] = 0x01; data_buf[1] = 0x00 # set 1 line inversion
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(10)
        reg_buf[1] = _ENTRY_MODE; data_buf[0] = 0x10; data_buf[1] = 0x30 # set GRAM write direction and BGR=1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(10)
        reg_buf[1] = _DISP_CTRL1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # display off
        time.sleep_ms(10)
        reg_buf[1] = _BLANK_PERIOD_CTRL1; data_buf[0] = 0x08; data_buf[1] = 0x08 # set back porch and front porch
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(10)
        reg_buf[1] = _FRAME_CYCLE_CTRL; data_buf[0] = 0x11; data_buf[1] = 0x00 # set clocks number per line
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(10)
        reg_buf[1] = _INTERFACE_CTRL; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # CPU interface
        time.sleep_ms(10)
        reg_buf[1] = _OSC_CTRL; data_buf[0] = 0x0D; data_buf[1] = 0x01 # set osc
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(10)
        reg_buf[1] = _VCI_RECYCLING; data_buf[0] = 0x00; data_buf[1] = 0x20 # set VCI recycling
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(10)
        reg_buf[1] = _RAM_ADDR_SET1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # set RAM address
        reg_buf[1] = _RAM_ADDR_SET2; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # set RAM address
        # Set GRAM area
        reg_buf[1] = _GATE_SCAN_CTRL; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _VERTICAL_SCROLL_CTRL1; data_buf[0] = 0x00; data_buf[1] = 0xDB; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _VERTICAL_SCROLL_CTRL2; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _VERTICAL_SCROLL_CTRL3; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _PARTIAL_DRIVING_POS1; data_buf[0] = 0x00; data_buf[1] = 0xDB; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _PARTIAL_DRIVING_POS2; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _HORIZONTAL_WINDOW_ADDR1; data_buf[0] = 0x00; data_buf[1] = 0xAF; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _HORIZONTAL_WINDOW_ADDR2; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _VERTICAL_WINDOW_ADDR1; data_buf[0] = 0x00; data_buf[1] = 0xDB; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _VERTICAL_WINDOW_ADDR2; data_buf[0] = 0x00; data_buf[1] = 0x20; _dc_high(); _write(data_buf_0x000)
        # Adjust GAMMA curve
        reg_buf[1] = _GAMMA_CTRL1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _GAMMA_CTRL2; data_buf[0] = 0x08; data_buf[1] = 0x08; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _GAMMA_CTRL3; data_buf[0] = 0x08; data_buf[1] = 0x0A; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _GAMMA_CTRL4; data_buf[0] = 0x00; data_buf[1] = 0x0A; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _GAMMA_CTRL5; data_buf[0] = 0x0A; data_buf[1] = 0x08; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _GAMMA_CTRL6; data_buf[0] = 0x08; data_buf[1] = 0x08; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _GAMMA_CTRL7; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _GAMMA_CTRL8; data_buf[0] = 0x0A; data_buf[1] = 0x00; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _GAMMA_CTRL9; data_buf[0] = 0x07; data_buf[1] = 0x10; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _GAMMA_CTRL10; data_buf[0] = 0x07; data_buf[1] = 0x10; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _DISP_CTRL1; data_buf[0] = 0x00; data_buf[1] = 0x12; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        time.sleep_ms(50)
        reg_buf[1] = _DISP_CTRL1; data_buf[0] = 0x10; data_buf[1] = 0x17; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        _cs.high()

    @micropython.viper
    def _clear(self):
        '''clear screen; called by self.__init__'''
        self.fill_rect(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT, _COLOR_LIGHT)
        time.sleep_ms(10)

    @micropython.viper
    def _reset(self):
        '''reset screen; called by self.__init__'''
        _rst = rst
        _rst.high()  # pull reset pin high to release from reset status
        time.sleep_ms(1)
        _rst.low()   # pull reset pin low to reset
        time.sleep_ms(10)
        _rst.high()  # pull reset pin high to release from reset status
        time.sleep_ms(50)

    @micropython.viper
    def _set_window(self, x0: int, y0: int, x1: int, y1: int):
        '''set draw window; called by self.rect, self.fill_rect, self.hline, self.vline and self.draw_bit_buffer'''
        x0 = _DISPLAY_WIDTH - x0 - 1; x1 = _DISPLAY_WIDTH - x1 - 1
        y0 = _DISPLAY_HEIGHT - y0 - 1; y1 = _DISPLAY_HEIGHT - y1 - 1
        reg_buf = bytearray(2); data_buf = bytearray(2)
        _write = spi.write; _dc_low = dc.low; _dc_high = dc.high
        data = 0x1000 | (_BOTTOM_UP_R2L << 3)
        reg_buf[1] = _ENTRY_MODE; data_buf[0] = data >> 8; data_buf[1] = data & 0xFF # BGR | I/D | AM
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        y0_0 = y0 >> 8; y0_1 = y0 & 0xFF
        reg_buf[1] = _HORIZONTAL_WINDOW_ADDR1; data_buf[0] = y0_0; data_buf[1] = y0_1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _HORIZONTAL_WINDOW_ADDR2; data_buf[0] = y1 >> 8; data_buf[1] = y1 & 0xFF
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        x0_0 = x0 >> 8; x0_1 = x0 & 0xFF
        reg_buf[1] = _VERTICAL_WINDOW_ADDR1; data_buf[0] = x0_0; data_buf[1] = x0_1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _VERTICAL_WINDOW_ADDR2; data_buf[0] = x1 >> 8; data_buf[1] = x1 & 0xFF
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _RAM_ADDR_SET1; data_buf[0] = y0_0; data_buf[1] = y0_1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _RAM_ADDR_SET2; data_buf[0] = x0_0; data_buf[1] = x0_1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _GRAM_DATA_REG; _dc_low(); _write(reg_buf)

class Font(object):
    '''font class; initiated once by display.__init__'''

    def __init__(self, scr, font) -> None:
        self._scr = scr
        self._font = font
        buffer = bytearray(4)
        self._palette_buffer = buffer
        self._palette = framebuf.FrameBuffer(buffer, 2, 1, framebuf.RGB565)

    @micropython.viper
    def text_box(self, x: int, y: int, w: int, h: int, text, color: int, align: int, frame_buffer):
        '''draw text to frame buffer within a set of bounding coordinates; called by ui_blocks: *.draw, TextEdit._draw_input_text and
        TextEdit._draw_selection'''
        _tw, _th = self.get_text_bounds(text)
        tw = int(_tw)
        th = int(_th)
        if align == _ALIGN_CENTRE:
            x += (w - tw) // 2
        elif align != _ALIGN_LEFT:
            x += w - tw
        y += (h - th) // 2
        background = abs(color - 1)
        self._write(text, x, y, color, background, frame_buffer)

    @micropython.viper
    def vertical_text_box(self, x: int, y: int, w: int, h: int, text, color: int, align: int, frame_buffer):
        '''draw text vertically to frame buffer within a set of bounding coordinates; called by PageTabs.draw'''
        tw = 0
        th = 0
        for char in text:
            _cw, _ch = self.get_text_bounds(char)
            cw = int(_cw)
            ch = int(_ch)
            tw = int(max(tw, cw))
            th += ch
        if align == _ALIGN_CENTRE:
            x += (w - tw) // 2
        elif align != _ALIGN_LEFT:
            x += w - tw
        y += (h - th) // 2
        background = abs(color - 1)
        for char in text:
            _cw, _ch = self.get_text_bounds(char)
            cw = int(_cw)
            ch = int(_ch)
            lx = x
            if align == _ALIGN_CENTRE:
                lx += (tw - cw) // 2
            elif align != _ALIGN_LEFT:
                lx += tw - cw
            self._write(char, lx, y, color, background, frame_buffer)
            y += ch

    @micropython.viper
    def get_text_bounds(self, text):
        '''return width and height of text (without drawing it); called by self.text_box, self.get_text_box_bounds and
        TextEdit._draw_input_text'''
        if int(len(text)) == 0:
            return 0, 0
        w = 0
        for char in text:
            _, _, tw = self._font.get_ch(char)
            w += int(tw)
        return w, self._font.HEIGHT

    @micropython.viper
    def get_text_box_bounds(self, x: int, y: int, w: int, h: int, text, align: int):
        '''return bounding coordinates of the text itself if drawing it within a set of bounding coordinates (without drawing it);
        called by TextEdit._draw_input_text'''
        _tw, _th = self.get_text_bounds(text)
        tw = int(_tw)
        th = int(_th)
        if align == _ALIGN_CENTRE:
            x += (w - tw) // 2
        elif align != _ALIGN_LEFT:
            x += w - tw
        y += (h - th) // 2
        return x, y, tw, th

    @micropython.viper
    def _write(self, text, x: int, y:int, fore_color: int, back_color: int, frame_buffer):
        '''draw text to frame buffer; called by self.text_box'''
        if int(len(text)) == 0:
            return
        for char in text:
            tw = self._put_char(char, x, y, fore_color, back_color, frame_buffer)
            x += int(tw)

    @micropython.viper
    def _put_char(self, char, x: int, y: int, fore_color: int, back_color: int, frame_buffer) -> int:
        '''draw character to frame buffer; called by self._write'''
        glyph, _th, _tw = self._font.get_ch(char)
        th = int(_th)
        tw = int(_tw)
        if tw == 0:
            return 0
        _palette = self._palette
        _palette.pixel(0, 0, back_color)
        _palette.pixel(1, 0, fore_color)
        buffer = bytearray(glyph)
        ch_buffer = framebuf.FrameBuffer(buffer, tw, th, framebuf.MONO_HLSB)
        frame_buffer.blit(ch_buffer, x, y, back_color, _palette)
        return tw