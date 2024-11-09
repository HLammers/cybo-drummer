''' Library providing settings pages class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

from data_types import GenOptions
import ui
from ui_pages import Page
from ui_blocks import TitleBar, EmptyRow, ButtonBlock, SelectBlock

_NONE                     = const(-1)

_NR_IN_PORTS              = const(6)
_NR_OUT_PORTS             = const(6)

_ON_OFF_OPTIONS           = ('off', 'on')
_INPUT_PORT_OPTIONS       = GenOptions(_NR_IN_PORTS, 1, ('_',), str)
_OUTPUT_PORT_OPTIONS      = GenOptions(_NR_OUT_PORTS, 1, ('_',), str)
_CHANNEL_OPTIONS          = GenOptions(16, 1, ('__',), str)

_SUB_PAGES                = const(2)
_SUB_PAGE_MIDI_THRU       = const(0)
_SUB_PAGE_OTHER           = const(1)

_SELECT_SUB_PAGE          = const(-1)
_MIDI_THRU                = const(0)
_MIDI_THRU_INPUT_PORT     = const(1)
_MIDI_THRU_INPUT_CHANNEL  = const(2)
_MIDI_THRU_OUTPUT_PORT    = const(3)
_MIDI_THRU_OUTPUT_CHANNEL = const(4)
_OTHER_MIDI_LEARN         = const(0)
_OTHER_MIDI_LEARN_PORT    = const(1)
_OTHER_DEFAULT_VOLUME     = const(2)
_OTHER_STORE_BACK_UP      = const(3)
_OTHER_RESTORE_BACK_UP    = const(4)
_OTHER_FACTORY_RESET      = const(5)
_OTHER_ABOUT              = const(6)

_POP_UP_CONFIRM           = const(3)
_POP_UP_ABOUT             = const(4)

class PageSettings(Page):
    '''settings page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, visible)
        ###### only for testing or screenshot
        # self.sub_page = 1
        self.page_is_built = False
        self._build_page()

    def program_change(self) -> None:
        '''update page after program change (also needed to trigger draw); called by ui.program_change'''
        if self.visible:
            self._load()
        else:
            selected_block = self.selected_block
            blocks = self.blocks
            if selected_block != 0:
                blocks[selected_block].update(redraw=False)
                blocks[0].update(True, redraw=False)
            self.selected_block = 0

    def process_user_input(self, id: int, value: int = _NONE, text: str = '',
                           button_encoder_0: bool = False, button_encoder_1: bool = False) -> None:
        '''process user input at page level (ui.ui.set_user_input_dict > global user_input_dict > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        if id == _SELECT_SUB_PAGE:
            if button_encoder_0 or button_encoder_1 or value == _NONE or value == self.sub_page:
                return
            self._set_sub_page(value)
            self._load()
            return
        if self.sub_page == _SUB_PAGE_MIDI_THRU:
            if button_encoder_0 or button_encoder_1:
                return
            elif value != _NONE:
                _data = ui.data
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
                else:
                    return
                _data.save_data_json_file()
                ui.router.update(False, False, False, False, False, False)
        else: # self.sub_page == _SUB_PAGE_OTHER
            if button_encoder_0:
                return
            elif button_encoder_1:
                if id == _OTHER_STORE_BACK_UP:
                    message = 'not saved, sure?' if ui.router.program_changed else 'store back-up?'
                    ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _OTHER_STORE_BACK_UP, message, self._callback_confirm)
                elif id == _OTHER_RESTORE_BACK_UP:
                    ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _OTHER_RESTORE_BACK_UP, 'restore back-up?', self._callback_confirm)
                elif id == _OTHER_FACTORY_RESET:
                    ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _OTHER_FACTORY_RESET, 'factory reset?', self._callback_confirm)
                elif id == _OTHER_ABOUT:
                    ui.ui.pop_ups[_POP_UP_ABOUT].open(self, _OTHER_ABOUT)
            elif value != _NONE:
                _data = ui.data
                if id == _OTHER_MIDI_LEARN:
                    _data.settings['midi_learn'] = bool(value)
                elif id == _OTHER_MIDI_LEARN_PORT:
                    _data.settings['midi_learn_port'] = value - 1 # 0 becomes _NONE
                elif id == _OTHER_DEFAULT_VOLUME:
                    _data.settings['default_output_velocity'] = value
                else:
                    return
                _data.save_data_json_file()
                ui.router.update(False, False, False, False, False, False)

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__ and self._build_sub_page'''
        if self.sub_page is None or self.page_is_built:
            return
        self.page_is_built = True
        _build_sub_page = self._build_sub_page
        sub_pages_title_bars = self.sub_pages_title_bars
        sub_pages_blocks = self.sub_pages_blocks
        sub_pages_empty_blocks = self.sub_pages_empty_blocks
        for i in range(_SUB_PAGES):
            title_bar, blocks, empty_blocks = _build_sub_page(i)
            sub_pages_title_bars.append(title_bar)
            sub_pages_blocks.append(blocks)
            sub_pages_empty_blocks.append(empty_blocks)
        self._set_sub_page(self.sub_page)

    def _build_sub_page(self, sub_page: int) -> tuple:
        '''build sub-page (without drawing it); called by self._build_page'''
        if not self.page_is_built:
            self._build_page()
            return None, [], []
        blocks = []
        empty_blocks = []
        selected_block = self.selected_block
        _callback_input = self.callback_input
        if sub_page == _SUB_PAGE_MIDI_THRU:
            title_bar = TitleBar('settings: midi thru', 1, _SUB_PAGES)
            blocks.append(SelectBlock(_MIDI_THRU, 0, 0, 2, selected_block == _MIDI_THRU, 'midi thru', _ON_OFF_OPTIONS,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_MIDI_THRU_INPUT_PORT, 1, 0, 1, selected_block == _MIDI_THRU_INPUT_PORT, 'input port',
                                      _INPUT_PORT_OPTIONS, callback_func=_callback_input))
            blocks.append(SelectBlock(_MIDI_THRU_INPUT_CHANNEL, 1, 1, 1, selected_block == _MIDI_THRU_INPUT_CHANNEL, 'input channel',
                                      _CHANNEL_OPTIONS, callback_func=_callback_input))
            blocks.append(SelectBlock(_MIDI_THRU_OUTPUT_PORT, 2, 0, 1, selected_block == _MIDI_THRU_OUTPUT_PORT, 'output port',
                                      _OUTPUT_PORT_OPTIONS, callback_func=_callback_input))
            blocks.append(SelectBlock(_MIDI_THRU_OUTPUT_CHANNEL, 2, 1, 1, selected_block == _MIDI_THRU_OUTPUT_CHANNEL, 'output channel',
                                      _CHANNEL_OPTIONS, callback_func=_callback_input))
            empty_blocks.append(EmptyRow(_NONE, 3))
            empty_blocks.append(EmptyRow(_NONE, 4))
            empty_blocks.append(EmptyRow(_NONE, 5))
        else: # sub_page == SUB_PAGE_OTHER
            title_bar = TitleBar('settings: other', 2, _SUB_PAGES)
            blocks.append(SelectBlock(_OTHER_MIDI_LEARN, 0, 0, 1, selected_block == _OTHER_MIDI_LEARN, 'midi learn', _ON_OFF_OPTIONS,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_OTHER_MIDI_LEARN_PORT, 0, 1, 1, selected_block == _OTHER_MIDI_LEARN_PORT, 'midi learn port',
                                      _INPUT_PORT_OPTIONS, callback_func=_callback_input))
            blocks.append(SelectBlock(_OTHER_DEFAULT_VOLUME, 1, 0, 2, selected_block == _OTHER_DEFAULT_VOLUME, 'default output velocity',
                                      [str(i) for i in range(0, 127)], callback_func=_callback_input))
            blocks.append(ButtonBlock(_OTHER_STORE_BACK_UP, 2, 0, 1, selected_block == _OTHER_STORE_BACK_UP, 'store back-up',
                                      callback_func=_callback_input))
            blocks.append(ButtonBlock(_OTHER_RESTORE_BACK_UP, 2, 1, 1, self.selected_block == _OTHER_RESTORE_BACK_UP, 'restore back-up',
                                      callback_func=_callback_input))
            blocks.append(ButtonBlock(_OTHER_FACTORY_RESET, 3, 0, 1, selected_block == _OTHER_FACTORY_RESET, 'factory reset',
                                      callback_func=_callback_input))
            blocks.append(ButtonBlock(_OTHER_ABOUT, 3, 1, 1, selected_block == _OTHER_ABOUT, 'about', callback_func=_callback_input))
            empty_blocks.append(EmptyRow(_NONE, 4))
            empty_blocks.append(EmptyRow(_NONE, 5))
        return title_bar, blocks, empty_blocks

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change and Page*.process_user_input'''
        if ui.ui.active_pop_up is not None:
            redraw = False
        self._set_midi_thru_options()
        self._set_other_options()
        if redraw:
            self._draw()

    def _set_midi_thru_options(self) -> None:
        '''load and set options and values to input blocks on midi thru sub-page; called by self._load'''
        if self.sub_page != _SUB_PAGE_MIDI_THRU:
            return
        settings = ui.data.settings
        blocks = self.blocks
        blocks[_MIDI_THRU].set_options(selection=int(settings['midi_thru']), redraw=False)
        value = settings['midi_thru_input_port'] + 1 # _NONE becomes 0
        blocks[_MIDI_THRU_INPUT_PORT].set_options(selection=value, redraw=False)
        value = settings['midi_thru_input_channel'] + 1 # _NONE becomes 0
        blocks[_MIDI_THRU_INPUT_CHANNEL].set_options(selection=value, redraw=False)
        value = settings['midi_thru_output_port'] + 1 # _NONE becomes 0
        blocks[_MIDI_THRU_OUTPUT_PORT].set_options(selection=value, redraw=False)
        value = settings['midi_thru_output_channel'] + 1 # _NONE becomes 0
        blocks[_MIDI_THRU_OUTPUT_CHANNEL].set_options(selection=value, redraw=False)

    def _set_other_options(self) -> None:
        '''load and set options and values to input blocks on other options sub-page; called by self._load'''
        if self.sub_page != _SUB_PAGE_OTHER:
            return
        settings = ui.data.settings
        blocks = self.blocks
        blocks[_OTHER_MIDI_LEARN].set_options(selection=int(settings['midi_learn']), redraw=False)
        value = settings['midi_learn_port'] + 1 # _NONE becomes 0
        blocks[_OTHER_MIDI_LEARN_PORT].set_options(selection=value, redraw=False)
        blocks[_OTHER_DEFAULT_VOLUME].set_options(selection=settings['default_output_velocity'], redraw=False)

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.process_user_input'''
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_OTHER:
            if not confirm:
                return
            if caller_id == _OTHER_STORE_BACK_UP:
                ui.router.save_back_up()
            elif caller_id == _OTHER_RESTORE_BACK_UP:
                ui.router.restore_back_up()
            elif caller_id == _OTHER_FACTORY_RESET:
                ui.router.factory_reset()