''' Library providing monitor pages class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

from collections import deque

import ui
from ui_pages import Page
from ui_blocks import TitleBar, TextRow

_NONE              = const(-1)

_COLOR_DARK        = const(0xAA29) # 0x29AA dark purple blue
_COLOR_LIGHT       = const(0xD9CD) # 0xCDD9 light purple grey

_PAGE_W            = const(204) # _DISPLAY_W - _PAGES_W
_PAGE_H            = const(163) # _DISPLAY_H - _TITLE_BAR_H
_TITLE_BAR_H       = const(13)
_ROW_H             = const(13)
_MAX_ROWS          = const(12) # int(_PAGE_H / _ROW_H)
_TOP_MARGIN        = const(3) # int((_PAGE_H - _MAX_ROWS * _ROW_H) / 2)

_SUB_PAGES         = const(3)
_SUB_PAGE_ROUTING  = const(0)
_SUB_PAGE_MIDI_IN  = const(1)
# _SUB_PAGE_MIDI_OUT = const(2)

_SELECT_SUB_PAGE   = const(-1)

class PageMonitor(Page):
    '''monitor page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, visible)
        ###### only for testing or screenshot
        # self.sub_page = 0
        self.block_active = True
        self.font_type = None
        self.text_deques = [deque((), _MAX_ROWS - 1), deque((), _MAX_ROWS - 1), deque((), _MAX_ROWS - 1)]
        self.page_is_built = False
        self._build_page()

    def program_change(self) -> None:
        '''update page after program change (also needed to trigger draw); called by ui.program_change'''
        if self.visible:
            self._load()

    def process_user_input(self, id: int, value: int = _NONE, text: str = '',
                           button_encoder_0: bool = False, button_encoder_1: bool = False) -> None:
        '''process user input at page level (ui.ui.set_user_input_dict > global user_input_dict > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        if id == _SELECT_SUB_PAGE:
            if button_encoder_0 or button_encoder_1 or value is None or value == self.sub_page:
                return
            self._set_sub_page(value)
            self._reset_monitor()
            self._load()

    def add_to_monitor(self, type: int, text: str) -> None:
        '''add event to monitor deque (router.send_to_monitor > router.monitor_data > ui.process_monitor > PageMonitor.add_to_monitor); called
        by ui.process_monitor'''
        if not self.visible or self.sub_page != type:
            return
        self.text_deques[type].append(text)
        self._load()

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__'''
        if self.page_is_built:
            return
        self.page_is_built = True
        sub_pages_title_bars = self.sub_pages_title_bars
        sub_pages_empty_blocks = self.sub_pages_empty_blocks
        text_deques = self.text_deques
        for i in range(_SUB_PAGES):
            if i == _SUB_PAGE_ROUTING:
                sub_pages_title_bars.append(TitleBar('monitor routing', 1, _SUB_PAGES))
            elif i == _SUB_PAGE_MIDI_IN:
                sub_pages_title_bars.append(TitleBar('monitor midi in', 2, _SUB_PAGES))
            else: # i == _SUB_PAGE_MIDI_OUT
                sub_pages_title_bars.append(TitleBar('monitor midi out', 3, _SUB_PAGES))
            sub_pages_empty_blocks.append((_Monitor(i, text_deques[i]),))
        self.sub_pages_blocks = ((), (), ())
        self._set_sub_page(self.sub_page)

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change, Page*.process_user_input,
        PageMonitor.add_to_monitor'''
        if redraw:
            self._draw()

    def _reset_monitor(self):
        '''empty monitor deques; called by self.process_user_input'''
        text_deques = self.text_deques
        for i in range(3):
            while len(text_deques[i]) > 0:
                text_deques[i].pop()

class _Monitor():
    '''class providing the monitor part of a monitor sup-page; initiated by PageMonitor._build_page'''

    def __init__(self, id: int, text_deque) -> None:
        self.id = id
        self.text_deque = text_deque

    def draw(self) -> None:
        '''draw monitor part of monitor sub-page; called by PageMonitor._draw'''
        ui.scr.fill_rect(0, _TITLE_BAR_H, _PAGE_W, _TOP_MARGIN, _COLOR_DARK)
        y = _TITLE_BAR_H + _TOP_MARGIN
        for text in self.text_deque:
            TextRow().draw(0, y, _PAGE_W, _ROW_H, text, _COLOR_DARK, _COLOR_LIGHT)
            y += _ROW_H
        TextRow().draw(0, y, _PAGE_W, _ROW_H, '...', _COLOR_DARK, _COLOR_LIGHT)
        y += _ROW_H
        h = y - _TITLE_BAR_H - _TOP_MARGIN - _PAGE_H
        h = _PAGE_H - _TITLE_BAR_H - y
        h = _PAGE_H - y + _TITLE_BAR_H
        if h > 0:
            ui.scr.fill_rect(0, y, _PAGE_W, h, _COLOR_DARK)