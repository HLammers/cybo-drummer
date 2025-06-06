''' Library providing settings pages class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

_INITIAL_SUB_PAGE = const(0)

import main_loops as ml
from ui_pages import Page
from ui_blocks import TitleBar, ButtonBlock, CheckBoxBlock, SelectBlock, TextRow
from constants import INPUT_PORT_OPTIONS, OUTPUT_PORT_OPTIONS, CHANNEL_OPTIONS, VELOCITY_OPTIONS, TEXT_ROWS_SETTINGS

_NONE                     = const(-1)

_TEXT_ROW_Y               = const(163)
_TEXT_ROW_H               = const(13)

_BACK_COLOR               = const(0xAA29) # 0x29AA dark purple blue
_FORE_COLOR               = const(0xD9CD) # 0xCDD9 light purple grey

_ALIGN_CENTRE             = const(1)

_SUB_PAGES                = const(1)
_SUB_PAGE_SETTINGS        = const(0)

_SELECT_SUB_PAGE          = const(-1)
_MIDI_THRU                = const(0)
_MIDI_THRU_INPUT_PORT     = const(1)
_MIDI_THRU_INPUT_CHANNEL  = const(2)
_MIDI_THRU_OUTPUT_PORT    = const(3)
_MIDI_THRU_OUTPUT_CHANNEL = const(4)
_MIDI_LEARN               = const(5)
_MIDI_LEARN_PORT          = const(6)
_DEFAULT_VELOCITY         = const(7)
_STORE_BACK_UP            = const(8)
_RESTORE_BACK_UP          = const(9)
_FACTORY_RESET            = const(10)
_ABOUT                    = const(11)

_POP_UP_CONFIRM           = const(3)
_POP_UP_ABOUT             = const(9)

class PageSettings(Page):
    '''settings page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, _SUB_PAGES, visible)
        self.sub_page = _INITIAL_SUB_PAGE
        self.page_is_built = False
        self._build_page()

    def program_change(self, update_only: bool) -> None:
        '''update page after program change; called by ui.program_change'''
        if self.visible:
            self._load()
        else:
            blocks = self.blocks
            if (selected_block := self.selected_block[self.sub_page]) != 0:
                blocks[selected_block].update(False)
                blocks[0].update(True, False)

    def encoder(self, encoder_id: int, value: int, page_select_mode: bool) -> bool:
        '''process encoder input at page level (ui.process_encoder > Page.encoder/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if super().encoder(encoder_id, value, page_select_mode):
            self._set_text_row()
            return True
        return False

    def process_user_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> bool:
        '''process user input at page level (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        value = int(value)
        if id == _SELECT_SUB_PAGE:
            if button_del or button_sel_opt or value == _NONE or value == self.sub_page:
                return False
            self._set_sub_page(value)
            self._load()
            return True
        # if self.sub_page == _SUB_PAGE_SETTINGS:
        if button_del:
            return False
        elif button_sel_opt:
            if id == _STORE_BACK_UP:
                message = 'not saved, sure?' if ml.router.program_changed else 'store back-up?'
                ml.ui.pop_ups[_POP_UP_CONFIRM].open(self, _STORE_BACK_UP, message, self._callback_confirm)
            elif id == _RESTORE_BACK_UP:
                ml.ui.pop_ups[_POP_UP_CONFIRM].open(self, _RESTORE_BACK_UP, 'restore back-up?', self._callback_confirm)
            elif id == _FACTORY_RESET:
                ml.ui.pop_ups[_POP_UP_CONFIRM].open(self, _FACTORY_RESET, 'factory reset?', self._callback_confirm)
            elif id == _ABOUT:
                ml.ui.pop_ups[_POP_UP_ABOUT].open(self)
            else:
                return False
            return True
        elif value == _NONE:
            return False
        _ml = ml
        _data = _ml.data
        _router = _ml.router
        _router.handshake() # request second thread to wait
        if id == _MIDI_THRU:
            _data.settings['midi_thru'] = bool(value)
        elif id == _MIDI_THRU_INPUT_PORT:
            _data.settings['midi_thru_input_port'] = value - 1# 0 becomes _NONE
        elif id == _MIDI_THRU_INPUT_CHANNEL:
            _data.settings['midi_thru_input_channel'] = value - 1 # 0 becomes _NONE
        elif id == _MIDI_THRU_OUTPUT_PORT:
            _data.settings['midi_thru_output_port'] = value - 1 # 0 becomes _NONE
        elif id == _MIDI_THRU_OUTPUT_CHANNEL:
            _data.settings['midi_thru_output_channel'] = value - 1 # 0 becomes _NONE
        elif id == _MIDI_LEARN:
            _data.settings['midi_learn'] = bool(value)
        elif id == _MIDI_LEARN_PORT:
            _data.settings['midi_learn_port'] = value - 1 # 0 becomes _NONE
        elif id == _DEFAULT_VELOCITY:
            _data.settings['default_output_velocity'] = value
        else:
            _router.resume() # resume second thread
            return False
        _data.save_data_json_file()
        _router.update(already_waiting=True)
        return True

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__ and self._build_sub_page'''
        if self.sub_page is None or self.page_is_built:
            return
        self.page_is_built = True
        _build_sub_page = self._build_sub_page
        sub_pages_title_bars = self.sub_pages_title_bars
        sub_pages_blocks = self.sub_pages_blocks
        sub_pages_empty_blocks = self.sub_pages_empty_blocks
        sub_pages_text_rows = self.sub_pages_text_rows
        for i in range(_SUB_PAGES):
            title_bar, blocks, empty_blocks, text_row = _build_sub_page(i)
            sub_pages_title_bars.append(title_bar)
            sub_pages_blocks.append(blocks)
            sub_pages_empty_blocks.append(empty_blocks)
            sub_pages_text_rows.append(text_row)
        self._set_sub_page(self.sub_page)

    def _build_sub_page(self, sub_page: int) -> tuple:
        '''build sub-page (without drawing it); called by self._build_page'''
        if not self.page_is_built:
            self._build_page()
            return None, [], []
        blocks = []
        empty_blocks = []
        selected_block = self.selected_block[sub_page]
        _callback_input = self.callback_input
        # if sub_page == _SUB_PAGE_SETTINGS:
        title_bar = TitleBar('settings', 1, _SUB_PAGES)
        blocks.append(CheckBoxBlock(_MIDI_THRU, 0, 0, 1, 1, selected_block == _MIDI_THRU, 'midi thru', callback_func=_callback_input))
        blocks.append(SelectBlock(_MIDI_THRU_INPUT_PORT, 1, 0, 1, 4, selected_block == _MIDI_THRU_INPUT_PORT, 'in port',
                                  default_selection=0, callback_func=_callback_input))
        blocks.append(SelectBlock(_MIDI_THRU_INPUT_CHANNEL, 1, 1, 1, 4, selected_block == _MIDI_THRU_INPUT_CHANNEL, 'channel',
                                  default_selection=0, callback_func=_callback_input))
        blocks.append(SelectBlock(_MIDI_THRU_OUTPUT_PORT, 1, 2, 1, 4, selected_block == _MIDI_THRU_OUTPUT_PORT, 'out port',
                                  default_selection=0, callback_func=_callback_input))
        blocks.append(SelectBlock(_MIDI_THRU_OUTPUT_CHANNEL, 1, 3, 1, 4, selected_block == _MIDI_THRU_OUTPUT_CHANNEL, 'channel',
                                  default_selection=0, callback_func=_callback_input))
        blocks.append(CheckBoxBlock(_MIDI_LEARN, 2, 0, 1, 2, selected_block == _MIDI_LEARN, 'midi learn', callback_func=_callback_input))
        blocks.append(SelectBlock(_MIDI_LEARN_PORT, 2, 1, 1, 2, selected_block == _MIDI_LEARN_PORT, 'midi learn port',
                                  default_selection=0, callback_func=_callback_input))
        blocks.append(SelectBlock(_DEFAULT_VELOCITY, 3, 0, 1, 1, selected_block == _DEFAULT_VELOCITY, 'default output velocity',
                                  VELOCITY_OPTIONS, default_selection=64, callback_func=_callback_input))
        blocks.append(ButtonBlock(_STORE_BACK_UP, 4, 0, 1, 2, selected_block == _STORE_BACK_UP, 'store back-up',
                                  callback_func=_callback_input))
        blocks.append(ButtonBlock(_RESTORE_BACK_UP, 4, 1, 1, 2, selected_block == _RESTORE_BACK_UP, 'restore back-up',
                                  callback_func=_callback_input))
        blocks.append(ButtonBlock(_FACTORY_RESET, 5, 0, 1, 2, selected_block == _FACTORY_RESET, 'factory reset',
                                  callback_func=_callback_input))
        blocks.append(ButtonBlock(_ABOUT, 5, 1, 1, 2, selected_block == _ABOUT, 'about', callback_func=_callback_input))
        text_row = TextRow(_TEXT_ROW_Y, _TEXT_ROW_H, _BACK_COLOR, _FORE_COLOR, _ALIGN_CENTRE)
        return title_bar, blocks, empty_blocks, text_row

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change and Page*.process_user_input'''
        redraw &= ml.ui.active_pop_up is None
        self._set_options()
        if redraw:
            self._set_text_row(False)
            self.draw()

    def _set_text_row(self, redraw: bool = True) -> None:
        '''draw text row with long description of currently selected block; called by self.encoder and self._load'''
        self.text_row.set_text(TEXT_ROWS_SETTINGS[self.selected_block[self.sub_page]], redraw) # type: ignore

    def _set_options(self) -> None:
        '''load and set options and values to input blocks; called by self._load'''
        if self.sub_page != _SUB_PAGE_SETTINGS:
            return
        settings = ml.data.settings
        blocks = self.blocks
        blocks[_MIDI_THRU].set_checked((midi_thru := settings['midi_thru']), redraw=False)
        if midi_thru:
            block = blocks[_MIDI_THRU_INPUT_PORT]
            block.enable(True, redraw=False)
            block.set_options(INPUT_PORT_OPTIONS, settings['midi_thru_input_port'] + 1, redraw=False) # _NONE becomes 0
            block = blocks[_MIDI_THRU_INPUT_CHANNEL]
            block.enable(True, redraw=False)
            block.set_options(CHANNEL_OPTIONS, settings['midi_thru_input_channel'] + 1, redraw=False) # _NONE becomes 0
            block = blocks[_MIDI_THRU_OUTPUT_PORT]
            block.enable(True, redraw=False)
            block.set_options(OUTPUT_PORT_OPTIONS, settings['midi_thru_output_port'] + 1, redraw=False) # _NONE becomes 0
            block = blocks[_MIDI_THRU_OUTPUT_CHANNEL]
            block.enable(True, redraw=False)
            block.set_options(CHANNEL_OPTIONS, settings['midi_thru_output_channel'] + 1, redraw=False) # _NONE becomes 0
        else:
            block = blocks[_MIDI_THRU_INPUT_PORT]
            block.enable(False, redraw=False)
            block.set_options((), redraw=False)
            block = blocks[_MIDI_THRU_INPUT_CHANNEL]
            block.enable(False, redraw=False)
            block.set_options((), redraw=False)
            block = blocks[_MIDI_THRU_OUTPUT_PORT]
            block.enable(False, redraw=False)
            block.set_options((), redraw=False)
            block = blocks[_MIDI_THRU_OUTPUT_CHANNEL]
            block.enable(False, redraw=False)
            block.set_options((), redraw=False)
        blocks[_MIDI_LEARN].set_checked((midi_learn := settings['midi_learn']), redraw=False)
        block = blocks[_MIDI_LEARN_PORT]
        if midi_learn:
            block.enable(True, redraw=False)
            block.set_options(INPUT_PORT_OPTIONS, settings['midi_learn_port'] + 1, redraw=False) # _NONE becomes 0
        else:
            block.enable(False, redraw=False)
            block.set_options((), redraw=False)
        blocks[_DEFAULT_VELOCITY].set_options(selection=settings['default_output_velocity'], redraw=False)

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.process_user_input'''
        if not confirm:
            return
        if self.sub_page == _SUB_PAGE_SETTINGS:
            if caller_id == _STORE_BACK_UP:
                ml.data.save_back_up()
            elif caller_id == _RESTORE_BACK_UP:
                ml.data.restore_back_up()
            elif caller_id == _FACTORY_RESET:
                ml.data.factory_reset()