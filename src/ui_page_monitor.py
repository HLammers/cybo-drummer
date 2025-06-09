''' Library providing monitor pages class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

_INITIAL_SUB_PAGE = const(0)

import micropython
import framebuf

import main_loops as ml
from ui_pages import Page
from ui_blocks import TitleBar

_NONE              = const(-1)

_ASCII_DOT         = const(46)

_COLOR_DARK        = const(0xAA29) # 0x29AA dark purple blue
_COLOR_LIGHT       = const(0xD9CD) # 0xCDD9 light purple grey

_DISPLAY_WIDTH     = const(220)
_PAGE_W            = const(204) # _DISPLAY_W - _PAGES_W
_PAGE_H            = const(163) # _DISPLAY_H - _TITLE_BAR_H
_NET_PAGE_H        = const(160) # _PAGE_H - _TOP_MARGIN
_TITLE_BAR_H       = const(13)
_ROW_H             = const(12)
_MAX_ROWS          = const(12) # _PAGE_H // _ROW_H - 1
_TOP_MARGIN        = const(3) # (_PAGE_H - (_MAX_ROWS + 1) * _ROW_H) // 2
_FONT_WIDTH        = const(6)
_FONT_HEIGHT       = const(8)
# _GROSS_ROW_H       = const(15) # _ROW_H + (_ROW_H - _FONT_HEIGHT) // 2

_SUB_PAGES         = const(3)
_SUB_PAGE_ROUTING  = const(0)
_SUB_PAGE_MIDI_IN  = const(1)
# _SUB_PAGE_MIDI_OUT = const(2)

_SELECT_SUB_PAGE   = const(-1)

class PageMonitor(Page):
    '''monitor page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, _SUB_PAGES, visible)
        self.sub_page = _INITIAL_SUB_PAGE
        self.block_active = True
        self.row = 0
        self.row_length = 0
        self.frame_buffer = None
        self.page_is_built = False
        self._build_page()

    def program_change(self, update_only: bool) -> None:
        '''update page after program change; called by ui.program_change'''
        if self.frame_buffer is None:
            _FrameBuffer = framebuf.FrameBuffer
            print(_TITLE_BAR_H * _DISPLAY_WIDTH * 2, (_TITLE_BAR_H + _TOP_MARGIN) * _DISPLAY_WIDTH * 2, _TOP_MARGIN)
            self.frame_buffer = _FrameBuffer(ml.ui.display.byte_buffer[(_TITLE_BAR_H + _TOP_MARGIN) * _DISPLAY_WIDTH * 2:], _PAGE_W,
                                             _NET_PAGE_H, (RGB565 := framebuf.RGB565), _DISPLAY_WIDTH)
            self._palette = (_palette := _FrameBuffer(bytearray(4), 2, 1, RGB565))
            _palette.pixel(0, 0, _COLOR_DARK)
            _palette.pixel(1, 0, _COLOR_LIGHT)
        if self.visible:
            self._reset_monitor()

    def restore(self):
        '''redraw blocks on page; called by ui.process_user_input'''
        self._reset_monitor()

    def process_user_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> bool:
        '''process user input at page level (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        value = int(value)
        if id == _SELECT_SUB_PAGE:
            if button_del or button_sel_opt or value == _NONE or value == self.sub_page:
                return False
            self._set_sub_page(value)
            self._reset_monitor()
            return True
        return False

    @micropython.viper
    def add_to_monitor(self, type: int, text) -> bool:
        '''add event to monitor deque (router.send_to_monitor > router.monitor_data > ui.process_monitor > PageMonitor.add_to_monitor); called
        by ui.process_monitor'''
        if not bool(self.visible) or int(self.sub_page) != type:
            return False
        _frame_buffer = self.frame_buffer
        if (row := int(self.row)) == _MAX_ROWS:
            _frame_buffer.scroll(0, -_ROW_H) # type: ignore
            _frame_buffer.rect(0, (y := _MAX_ROWS * _ROW_H), int(self.row_length) * _FONT_WIDTH + 1, _ROW_H, _COLOR_DARK, True) # type: ignore (temporary)
            y -= _ROW_H
        else:
            _frame_buffer.rect(0, (y := row * _ROW_H), 3 * _FONT_WIDTH, _ROW_H, _COLOR_DARK, True) # type: ignore (temporary)
            self.row = row + 1
        self.row_length = len(text)
        _display = ml.ui.display
        _get_ch = _display.font.get_ch
        _FrameBuffer = framebuf.FrameBuffer
        MONO_HLSB = framebuf.MONO_HLSB
        frame_buffer = self.frame_buffer
        _blit = frame_buffer.blit # type: ignore
        _palette = self._palette
        x = 1
        for char in text:
            ch_buffer = _FrameBuffer(bytearray(_get_ch(ord(char))), _FONT_WIDTH, _FONT_HEIGHT, MONO_HLSB)
            _blit(ch_buffer, x, y, _COLOR_DARK, _palette)
            x += _FONT_WIDTH
        ch_buffer = _FrameBuffer(bytearray(_get_ch(_ASCII_DOT)), _FONT_WIDTH, _FONT_HEIGHT, MONO_HLSB)
        x = 1
        y += _ROW_H
        for _ in range(3):
            _blit(ch_buffer, x, y, _COLOR_DARK, _palette)
            x += _FONT_WIDTH
        return True

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__'''
        if self.page_is_built:
            return
        self.page_is_built = True
        sub_pages_title_bars = self.sub_pages_title_bars
        for i in range(_SUB_PAGES):
            if i == _SUB_PAGE_ROUTING:
                sub_pages_title_bars.append(TitleBar('monitor routing', 1, _SUB_PAGES))
            elif i == _SUB_PAGE_MIDI_IN:
                sub_pages_title_bars.append(TitleBar('monitor midi in', 2, _SUB_PAGES))
            else: # i == _SUB_PAGE_MIDI_OUT
                sub_pages_title_bars.append(TitleBar('monitor midi out', 3, _SUB_PAGES))
        self.sub_pages_blocks = ((), (), ())
        self.sub_pages_empty_blocks = ((), (), ())
        self._set_sub_page(self.sub_page)

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change, Page*.process_user_input,
        PageMonitor.add_to_monitor'''
        if redraw:
            self._reset_monitor()

    def _reset_monitor(self):
        '''empty monitor deques; called by self.program_change, self.restore, self.process_user_input, self._load'''
        self.row = 0
        _display = ml.ui.display
        _display.rect(0, _TITLE_BAR_H, _PAGE_W, _PAGE_H, _COLOR_DARK, True) # type: ignore (temporary)
        frame_buffer = self.frame_buffer
        _blit = frame_buffer.blit # type: ignore
        _get_ch = _display.font.get_ch
        ch_buffer = framebuf.FrameBuffer(bytearray(_get_ch(_ASCII_DOT)), _FONT_WIDTH, _FONT_HEIGHT, framebuf.MONO_HLSB)
        _palette = self._palette
        x = 1
        for _ in range(3):
            _blit(ch_buffer, x, 0, _COLOR_DARK, _palette)
            x += _FONT_WIDTH