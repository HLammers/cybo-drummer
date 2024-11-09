''' Library providing page select tabs class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import ui
from ui_blocks import PageTabs
if __debug__: import screen_log

_NONE          = const(-1)

_PAGE_PROGRAM  = const(1)
_PAGE_INPUT    = const(2)
_PAGE_OUTPUT   = const(3)
_PAGE_MONITOR  = const(4)
_PAGE_SETTINGS = const(5)

_MAIN_FRAMES   = (_PAGE_PROGRAM, _PAGE_INPUT, _PAGE_OUTPUT, _PAGE_MONITOR, _PAGE_SETTINGS)
_PAGE_LABELS   = ('PRG', 'IN', 'OUT', 'MON', 'SET')

class PagesTabs():
    '''ui pages tab frame class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int) -> None:
        self.id = id
        self.pages_tab = PageTabs(x, y, w, h, _PAGE_LABELS, _MAIN_FRAMES.index(ui.ui.active_page))

    def set_page_encoders(self, page_pressed: bool) -> None:
        '''switches value encoder input to or from page selection and changes colour of title bar (when page button is pressed); called by
        ui.process_user_input'''
        self.pages_tab.update(page_pressed)

    def encoder(self, value: int) -> None:
        '''process encoder input at pages tab level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if self.pages_tab.encoder(value):
            self.callback_input(self.id, value, _PAGE_LABELS[value])

    def program_change(self) -> None:
        '''update page after program change (needed to trigger draw); called by ui.program_change'''
        self.pages_tab.draw()

    def set_page(self, value: int) -> None:
        '''set, initiate and draw active page (ui._callback_encoder_0/_callback_encoder_1 > global encoder_input_0/encoder_input_1 >
        ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by ui.process_encoder_input'''
        if __debug__: screen_log.add_marker(f'set page to {_PAGE_LABELS[value]}')
        self.selection = value
        self.encoder(value)
        ui.ui.frames[ui.ui.active_page].set_visibility(False)
        ui.ui.active_page = ui.ui.pages[value].id
        ui.ui.frames[ui.ui.active_page].set_visibility(True)

    def process_user_input(self, id: int, value: int  = _NONE, text: str = '',
                           button_encoder_0: bool = False, button_encoder_1: bool = False) -> None:
        '''process user input at pages tab level (ui.ui.set_user_input_dict > global user_input_dict > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        pass

    def callback_input(self, id: int, value: int = _NONE, text: str = '', button_encoder_0: bool = False, button_encoder_1: bool = False) -> None:
        '''callback function for encoder input and blocks offering user input (ui._callback_button/Page/PagesTab.callback_input > ui.ui.set_user_input_dict >
        global user_input_dict > ui.process_user_input > Page/PagesTab.process_user_input); called (passed on) by self.encoder'''
        ui.set_user_input_dict({'frame_id': self.id, 'block_id': id, 'value': value, 'text': text,
                                'button_encoder_0': button_encoder_0, 'button_encoder_1': button_encoder_1, 'frame_select': False})
