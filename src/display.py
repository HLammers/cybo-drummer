''' Display library for Cybo-Drummer - Humanize Those Drum Computers!
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
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
    This library is highly optimized for speed and memory use when integrated into Cybo-Drummer. The class ‘ILI9225’ started off as an
    adaptation of:
        RaspberryPiPicoGFX, copyright (c) Michael Minor, https://github.com/9MMMinor/RaspberryPiPicoGFX/
    The class ‘Font’ started off as an adaptation of exFBfont, copyright (c) Owen Carter,
        https://github.com/easytarget/microPyEZfonts/blob/main/ezFBfont.py, which in turn is a reworked version of the class ‘Writer’,
        copyright (c) 2019-2021 Peter Hinch, https://github.com/peterhinch/micropython-font-to-py'''

import micropython
import time
import framebuf
from machine import Pin, SPI
import os

_DISPLAY_WIDTH        = const(220)
_DISPLAY_HEIGHT       = const(176)

_MAX_BUFFER_SIZE      = const(77440) # _DISPLAY_WIDTH * _DISPLAY_HEIGHT * 2

# _TOP_DOWN_L2R         = const(7)

# ILI9225 LCD Registers
_DRIVER_OUTPUT_CTRL   = const(0x01)  # Driver Output Control
_LCD_AC_DRIVING_CTRL  = const(0x02)  # LCD AC Driving Control
_ENTRY_MODE           = const(0x03)  # Entry Mode
_DISP_CTRL1           = const(0x07)  # Display Control 1
_BLANK_PERIOD_CTRL1   = const(0x08)  # Blank Period Control
_FRAME_CYCLE_CTRL     = const(0x0B)  # Frame Cycle Control
_INTERFACE_CTRL       = const(0x0C)  # Interface Control
_OSC_CTRL             = const(0x0F)  # Osc Control
_POWER_CTRL1          = const(0x10)  # Power Control 1
_POWER_CTRL2          = const(0x11)  # Power Control 2
_POWER_CTRL3          = const(0x12)  # Power Control 3
_POWER_CTRL4          = const(0x13)  # Power Control 4
_POWER_CTRL5          = const(0x14)  # Power Control 5
_VCI_RECYCLING        = const(0x15)  # VCI Recycling
_RAM_ADDR_SET1        = const(0x20)  # Horizontal GRAM Address Set
_RAM_ADDR_SET2        = const(0x21)  # Vertical GRAM Address Set
_GRAM_DATA_REG        = const(0x22)  # GRAM Data Register
_GATE_SCAN_CTRL       = const(0x30)  # Gate Scan Control Register
_VER_SCROLL_CTRL1     = const(0x31)  # Vertical Scroll Control 1 Register
_VER_SCROLL_CTRL2     = const(0x32)  # Vertical Scroll Control 2 Register
_VER_SCROLL_CTRL3     = const(0x33)  # Vertical Scroll Control 3 Register
_PARTIAL_DRIVING_POS1 = const(0x34)  # Partial Driving Position 1 Register
_PARTIAL_DRIVING_POS2 = const(0x35)  # Partial Driving Position 2 Register
_HOR_WINDOW_ADDR1     = const(0x36)  # Horizontal Address Start Position
_HOR_WINDOW_ADDR2     = const(0x37)  # Horizontal Address End Position
_VER_WINDOW_ADDR1     = const(0x38)  # Vertical Address Start Position
_VER_WINDOW_ADDR2     = const(0x39)  # Vertical Address End Position
_GAMMA_CTRL1          = const(0x50)  # Gamma Control 1
_GAMMA_CTRL2          = const(0x51)  # Gamma Control 2
_GAMMA_CTRL3          = const(0x52)  # Gamma Control 3
_GAMMA_CTRL4          = const(0x53)  # Gamma Control 4
_GAMMA_CTRL5          = const(0x54)  # Gamma Control 5
_GAMMA_CTRL6          = const(0x55)  # Gamma Control 6
_GAMMA_CTRL7          = const(0x56)  # Gamma Control 7
_GAMMA_CTRL8          = const(0x57)  # Gamma Control 8
_GAMMA_CTRL9          = const(0x58)  # Gamma Control 9
_GAMMA_CTRL10         = const(0x59)  # Gamma Control 10

_COLOR_LIGHT          = const(0xD9CD) # 0xCDD9 light purple grey

_FONT_WIDTH           = const(6)
_FONT_HEIGHT          = const(8)
_ALIGN_LEFT           = const(0)
_ALIGN_CENTRE         = const(1)
# _ALIGN_RIGHT          = const(2)

class Display(framebuf.FrameBuffer):
    '''class providing diplay buffer and draw functions; initiated once by ui.__init__'''

    def __init__(self, spi_id: int, baudrate: int, dc_pin: Pin, rst_pin: Pin, backlight_pin: Pin, font) -> None:
        self.spi = SPI(spi_id, baudrate=baudrate)
        self.dc = dc_pin
        self.rst = rst_pin
        self.backlight = backlight_pin
        self.font = font
        backlight_pin.off()
        rst_pin.init(rst_pin.OUT, value=0)
        dc_pin.init(dc_pin.OUT, value=0)
        self.byte_buffer = (byte_buffer := memoryview(bytearray(_MAX_BUFFER_SIZE)))
        super().__init__(byte_buffer, _DISPLAY_WIDTH, _DISPLAY_HEIGHT, (RGB565 := framebuf.RGB565))
        self._reset()
        self._setup()
        self._clear()
        self._palette = framebuf.FrameBuffer(bytearray(4), 2, 1, RGB565)
        backlight_pin.on()

    @micropython.viper
    def set_display(self, flag: bool):
        '''turn display on or off (excluding backlight); called by ui.check_sleep_time_out and ui._wake_up'''
        reg_buf = bytearray(2); data_buf = bytearray(2); data_buf_0x000 = bytearray(2)
        _write = self.spi.write; _dc = self.dc; _dc_low = _dc.low; _dc_high = _dc.high; _sleep_ms = time.sleep_ms
        reg_buf[1] = 0xFF; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        if flag:
            reg_buf[1] = _POWER_CTRL1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
            _sleep_ms(50)
            reg_buf[1] = _DISP_CTRL1; data_buf[0] = 0x10; data_buf[1] = 0x17; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
            _sleep_ms(200)
            self.backlight.on()
        else:
            self.backlight.off()
            reg_buf[1] = _DISP_CTRL1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
            _sleep_ms(50)
            reg_buf[1] = _POWER_CTRL1; data_buf[0] = 0x00; data_buf[1] = 0x03
            _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
            _sleep_ms(200)

    @micropython.viper
    def text_box(self, x: int, y: int, w: int, h: int, text, back_color: int, fore_color: int, align: int):
        '''draw text to frame buffer within a set of bounding coordinates; called by ui_blocks: *.draw, TextEdit._draw_input_text and
        TextEdit._draw_selection'''
        if (n := int(len(text))) == 0:
            return
        tw = n * _FONT_WIDTH - 1
        if align == _ALIGN_CENTRE:
            x += (w - tw) // 2
        elif align != _ALIGN_LEFT:
            x += w - tw
        y += (h - _FONT_HEIGHT) // 2
        _palette = self._palette
        _palette.pixel(0, 0, back_color)
        _palette.pixel(1, 0, fore_color)
        _FrameBuffer = framebuf.FrameBuffer
        _get_ch = self.font.get_ch
        MONO_HLSB = framebuf.MONO_HLSB
        _blit = self.blit
        for char in text:
            ch_buffer = _FrameBuffer(bytearray(_get_ch(ord(char))), _FONT_WIDTH, _FONT_HEIGHT, MONO_HLSB)
            _blit(ch_buffer, x, y, back_color, _palette)
            x += _FONT_WIDTH

    @micropython.viper
    def get_text_bounds(self, text):
        '''return width and height of text (without drawing it); called by TextEdit._draw_input_text'''
        if (n := int(len(text))) == 0:
            return 0, 0
        return n * _FONT_WIDTH - 1, _FONT_HEIGHT

    @micropython.viper
    def get_text_box_bounds(self, x: int, y: int, w: int, h: int, text, align: int):
        '''return bounding coordinates of the text itself if drawing it within a set of bounding coordinates (without drawing it);
        called by TextEdit._draw_input_text'''
        tw = int(len(text)) * _FONT_WIDTH - 1
        if align == _ALIGN_CENTRE:
            x += (w - tw) // 2
        elif align != _ALIGN_LEFT:
            x += w - tw
        y += (h - _FONT_HEIGHT) // 2
        return x, y, tw, _FONT_HEIGHT

    @micropython.native
    def draw_screen(self):
        '''draw display buffer to screen; called by main'''
        self._set_window(0, 0, _DISPLAY_WIDTH - 1, _DISPLAY_HEIGHT - 1)
        self.dc.high(); self.spi.write(self.byte_buffer[0:(_DISPLAY_WIDTH * _DISPLAY_HEIGHT * 2)])

    def save_screen_dump(self) -> None:
        '''save dump of current screen buffer to json file; called by ui.process_user_input'''
        i = 0
        while f'screen dump {i}.bin' in (files := os.listdir()):
            i += 1
        del files
        with open(f'screen dump {i}.bin', 'wb') as file:
            file.write(self.byte_buffer)
        print(f"screendump saved as 'screen dump {i}.bin'")
        self.set_display(False)
        time.sleep_ms(300)
        self.set_display(True)

    def delete(self):
        self.spi.deinit()
        del self.byte_buffer

    @micropython.viper
    def _setup(self):
        '''screen set up routine; called by self.__init__'''
        reg_buf = bytearray(2); data_buf = bytearray(2); data_buf_0x000 = bytearray(2)
        _write = self.spi.write; _dc = self.dc; _dc_low = _dc.low; _dc_high = _dc.high; _sleep_ms = time.sleep_ms
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
        _sleep_ms(10)
        reg_buf[1] = _POWER_CTRL2; data_buf[0] = 0x10; data_buf[1] = 0x38 # set APON,PON,AON,VCI1EN,VC
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        _sleep_ms(50)
        reg_buf[1] = _DRIVER_OUTPUT_CTRL; data_buf[0] = 0x03; data_buf[1] = 0x1C # set display line number and display direction
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        _sleep_ms(10)
        reg_buf[1] = _LCD_AC_DRIVING_CTRL; data_buf[0] = 0x01; data_buf[1] = 0x00 # set 1 line inversion
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        _sleep_ms(10)
        reg_buf[1] = _ENTRY_MODE; data_buf[0] = 0x10; data_buf[1] = 0x30 # set GRAM write direction and BGR=1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        _sleep_ms(10)
        reg_buf[1] = _DISP_CTRL1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # display off
        _sleep_ms(10)
        reg_buf[1] = _BLANK_PERIOD_CTRL1; data_buf[0] = 0x08; data_buf[1] = 0x08 # set back porch and front porch
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        _sleep_ms(10)
        reg_buf[1] = _FRAME_CYCLE_CTRL; data_buf[0] = 0x11; data_buf[1] = 0x00 # set clocks number per line
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        _sleep_ms(10)
        reg_buf[1] = _INTERFACE_CTRL; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # CPU interface
        _sleep_ms(10)
        reg_buf[1] = _OSC_CTRL; data_buf[0] = 0x0D; data_buf[1] = 0x01 # set osc
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        _sleep_ms(10)
        reg_buf[1] = _VCI_RECYCLING; data_buf[0] = 0x00; data_buf[1] = 0x20 # set VCI recycling
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        _sleep_ms(10)
        reg_buf[1] = _RAM_ADDR_SET1; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # set RAM address
        reg_buf[1] = _RAM_ADDR_SET2; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000) # set RAM address
        # Set GRAM area
        reg_buf[1] = _GATE_SCAN_CTRL; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _VER_SCROLL_CTRL1; data_buf[0] = 0x00; data_buf[1] = 0xDB; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _VER_SCROLL_CTRL2; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _VER_SCROLL_CTRL3; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _PARTIAL_DRIVING_POS1; data_buf[0] = 0x00; data_buf[1] = 0xDB; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _PARTIAL_DRIVING_POS2; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _HOR_WINDOW_ADDR1; data_buf[0] = 0x00; data_buf[1] = 0xAF; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _HOR_WINDOW_ADDR2; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf_0x000)
        reg_buf[1] = _VER_WINDOW_ADDR1; data_buf[0] = 0x00; data_buf[1] = 0xDB; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _VER_WINDOW_ADDR2; data_buf[0] = 0x00; data_buf[1] = 0x20; _dc_high(); _write(data_buf_0x000)
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
        _sleep_ms(50)
        reg_buf[1] = _DISP_CTRL1; data_buf[0] = 0x10; data_buf[1] = 0x17; _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)

    @micropython.viper
    def _clear(self):
        '''clear screen; called by self.__init__'''
        self.fill(_COLOR_LIGHT)
        self.draw_screen()

    @micropython.viper
    def _reset(self):
        '''reset screen; called by self.__init__'''
        _rst = self.rst; _sleep_ms = time.sleep_ms
        _rst.high()  # pull reset pin high to release from reset status
        _sleep_ms(1)
        _rst.low()   # pull reset pin low to reset
        _sleep_ms(10)
        _rst.high()  # pull reset pin high to release from reset status
        _sleep_ms(50)

    @micropython.viper
    def _set_window(self, x0: int, y0: int, x1: int, y1: int):
        '''set draw window; called by self.draw_screen'''
        reg_buf = bytearray(2); data_buf = bytearray(2)
        _write = self.spi.write; _dc = self.dc; _dc_low = _dc.low; _dc_high = _dc.high
        data = 0x1038 # 0x1000 | (_TOP_DOWN_L2R << 3) # BGR | I/D | AM
        reg_buf[1] = _ENTRY_MODE; data_buf[0] = data >> 8; data_buf[1] = data & 0xFF
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _HOR_WINDOW_ADDR1; data_buf[0] = y1 >> 8; data_buf[1] = y1 & 0xFF
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        y0_0 = y0 >> 8; y0_1 = y0 & 0xFF
        reg_buf[1] = _HOR_WINDOW_ADDR2; data_buf[0] = y0_0; data_buf[1] = y0_1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _VER_WINDOW_ADDR1; data_buf[0] = x1 >> 8; data_buf[1] = x1 & 0xFF
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        x0_0 = x0 >> 8; x0_1 = x0 & 0xFF
        reg_buf[1] = _VER_WINDOW_ADDR2; data_buf[0] = x0_0; data_buf[1] = x0_1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _RAM_ADDR_SET1; data_buf[0] = y0_0; data_buf[1] = y0_1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _RAM_ADDR_SET2; data_buf[0] = x0_0; data_buf[1] = x0_1
        _dc_low(); _write(reg_buf); _dc_high(); _write(data_buf)
        reg_buf[1] = _GRAM_DATA_REG; _dc_low(); _write(reg_buf)